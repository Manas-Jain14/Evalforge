from copy import deepcopy
from uuid import uuid4


def register_and_login(client, email):
    registration = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "correct-horse-battery"},
    )
    assert registration.status_code == 201
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "correct-horse-battery"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def create_project_and_key(client, user_headers, name="Phase 2"):
    project = client.post(
        "/api/v1/projects",
        headers=user_headers,
        json={"name": name},
    )
    assert project.status_code == 201
    project_id = project.json()["id"]
    key_response = client.post(
        f"/api/v1/projects/{project_id}/api-keys",
        headers=user_headers,
    )
    assert key_response.status_code == 201
    return project_id, key_response.json()


def batch(trace_id=None, root_id=None, child_id=None, event_id=None):
    trace_id = trace_id or str(uuid4())
    root_id = root_id or str(uuid4())
    child_id = child_id or str(uuid4())
    event_id = event_id or str(uuid4())
    return {
        "schema_version": "1",
        "batch_id": "correlation-only",
        "traces": [
            {
                "id": trace_id,
                "name": "chat request",
                "status": "ok",
                "start_time": "2026-11-11T09:00:00Z",
                "end_time": "2026-11-11T09:00:02Z",
                "duration_ms": 2000,
                "attributes": {"environment": "test"},
            }
        ],
        "spans": [
            {
                "id": root_id,
                "trace_id": trace_id,
                "parent_span_id": None,
                "name": "request",
                "operation_type": "http",
                "status": "ok",
                "start_time": "2026-11-11T09:00:00Z",
                "end_time": "2026-11-11T09:00:02Z",
                "duration_ms": 2000,
            },
            {
                "id": child_id,
                "trace_id": trace_id,
                "parent_span_id": root_id,
                "name": "model call",
                "operation_type": "llm",
                "status": "ok",
                "start_time": "2026-11-11T09:00:00.100Z",
                "end_time": "2026-11-11T09:00:01.900Z",
                "duration_ms": 1800,
                "input_tokens": 12,
                "output_tokens": 8,
                "estimated_cost": 1000,
                "estimated_cost_currency": "USD",
            },
        ],
        "events": [
            {
                "id": event_id,
                "trace_id": trace_id,
                "span_id": child_id,
                "event_type": "custom",
                "name": "model completed",
                "timestamp": "2026-11-11T09:00:01.900Z",
                "message": "done",
            }
        ],
    }


def ingest(client, secret, payload):
    return client.post(
        "/api/v1/ingest/batch",
        headers={"Authorization": f"Bearer {secret}"},
        json=payload,
    )


def test_api_key_secret_is_returned_once_and_owner_bound(client):
    owner_headers = register_and_login(client, "key-owner@example.com")
    other_headers = register_and_login(client, "key-other@example.com")
    project_id, key = create_project_and_key(client, owner_headers)

    assert len(key["secret"].split(".")[1]) >= 43
    listed = client.get(
        f"/api/v1/projects/{project_id}/api-keys",
        headers=owner_headers,
    )
    assert listed.status_code == 200
    assert key["secret"] not in listed.text
    assert "key_hash" not in listed.text
    assert key["secret"] not in client.get(
        f"/api/v1/projects/{project_id}",
        headers=owner_headers,
    ).text
    assert client.get(
        f"/api/v1/projects/{project_id}/api-keys",
        headers=other_headers,
    ).status_code == 404
    assert client.delete(
        f"/api/v1/api-keys/{key['id']}",
        headers=other_headers,
    ).status_code == 404


def test_revoked_api_key_cannot_ingest(client):
    user_headers = register_and_login(client, "revoked@example.com")
    project_id, key = create_project_and_key(client, user_headers)

    revoked = client.delete(
        f"/api/v1/api-keys/{key['id']}",
        headers=user_headers,
    )
    assert revoked.status_code == 204
    assert client.delete(
        f"/api/v1/api-keys/{key['id']}",
        headers=user_headers,
    ).status_code == 204
    response = ingest(client, key["secret"], batch())
    assert response.status_code == 401


def test_ingest_trace_read_tree_and_project_isolation(client):
    owner_headers = register_and_login(client, "trace-owner@example.com")
    other_headers = register_and_login(client, "trace-other@example.com")
    project_id, key = create_project_and_key(client, owner_headers)
    payload = batch()

    response = ingest(client, key["secret"], payload)
    assert response.status_code == 200
    assert response.json()["inserted"] == {"traces": 1, "spans": 2, "events": 1}
    assert response.json()["batch_id"] == payload["batch_id"]
    assert response.json()["duplicates"] == {"traces": 0, "spans": 0, "events": 0}
    assert response.json().get("stored") is None

    trace_id = payload["traces"][0]["id"]
    detail = client.get(
        f"/api/v1/projects/{project_id}/traces/{trace_id}",
        headers=owner_headers,
    )
    assert detail.status_code == 200
    assert len(detail.json()["spans"]) == 1
    root = detail.json()["spans"][0]
    assert root["id"] == payload["spans"][0]["id"]
    assert root["children"][0]["id"] == payload["spans"][1]["id"]
    assert root["children"][0]["parent_span_id"] == root["id"]
    assert detail.json()["events"][0]["span_id"] == root["children"][0]["id"]
    assert detail.json()["spans"][0]["children"][0]["estimated_cost"] is None

    listed = client.get(
        f"/api/v1/projects/{project_id}/traces?offset=0&limit=10",
        headers=owner_headers,
    )
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [trace_id]
    assert client.get(
        f"/api/v1/projects/{project_id}/traces/{trace_id}",
        headers=other_headers,
    ).status_code == 404


def test_identical_replay_reports_duplicates_without_inserting(client):
    user_headers = register_and_login(client, "replay@example.com")
    _, key = create_project_and_key(client, user_headers)
    payload = batch()

    first = ingest(client, key["secret"], payload)
    second = ingest(client, key["secret"], deepcopy(payload))

    assert first.status_code == second.status_code == 200
    assert second.json()["inserted"] == {"traces": 0, "spans": 0, "events": 0}
    assert second.json()["duplicates"] == {"traces": 1, "spans": 2, "events": 1}


def test_conflicting_span_rolls_back_trace_in_same_batch(client):
    user_headers = register_and_login(client, "conflict@example.com")
    project_id, key = create_project_and_key(client, user_headers)
    original = batch()
    assert ingest(client, key["secret"], original).status_code == 200

    conflict = batch(
        trace_id=str(uuid4()),
        root_id=original["spans"][0]["id"],
    )
    conflict["spans"][0]["name"] = "different canonical content"
    response = ingest(client, key["secret"], conflict)
    assert response.status_code == 409
    traces = client.get(
        f"/api/v1/projects/{project_id}/traces",
        headers=user_headers,
    )
    assert len(traces.json()) == 1
    assert client.get(
        f"/api/v1/projects/{project_id}/traces/{conflict['traces'][0]['id']}",
        headers=user_headers,
    ).status_code == 404


def test_parent_span_from_another_trace_rejects_entire_batch(client):
    user_headers = register_and_login(client, "parent-link@example.com")
    project_id, key = create_project_and_key(client, user_headers)
    existing = batch()
    assert ingest(client, key["secret"], existing).status_code == 200

    invalid = batch()
    invalid["spans"][0]["parent_span_id"] = existing["spans"][0]["id"]
    response = ingest(client, key["secret"], invalid)
    assert response.status_code == 422
    assert len(
        client.get(
            f"/api/v1/projects/{project_id}/traces",
            headers=user_headers,
        ).json()
    ) == 1


def test_ingest_rejects_mismatched_project_and_unknown_fields(client):
    user_headers = register_and_login(client, "validation@example.com")
    _, key = create_project_and_key(client, user_headers)
    jwt_token = user_headers["Authorization"].split(" ", 1)[1]
    assert ingest(client, jwt_token, batch()).status_code == 401

    payload = batch()
    payload["project_id"] = str(uuid4())
    assert ingest(client, key["secret"], payload).status_code == 422

    payload = batch()
    payload["prompt"] = "must not be accepted"
    assert ingest(client, key["secret"], payload).status_code == 422

    payload = batch()
    payload["spans"][0]["attributes"] = {"nested": {"prompt": "must not be accepted"}}
    assert ingest(client, key["secret"], payload).status_code == 422


def test_ingest_batch_limits_return_payload_too_large(client):
    user_headers = register_and_login(client, "limits@example.com")
    _, key = create_project_and_key(client, user_headers)

    over_record_limit = batch()
    over_record_limit["traces"].extend(
        {**over_record_limit["traces"][0], "id": str(uuid4())}
        for _ in range(97)
    )
    assert ingest(client, key["secret"], over_record_limit).status_code == 413

    over_byte_limit = batch()
    over_byte_limit["batch_id"] = "x" * 1_000_001
    assert ingest(client, key["secret"], over_byte_limit).status_code == 413
