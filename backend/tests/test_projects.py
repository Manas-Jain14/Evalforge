from uuid import UUID


def register_and_login(client, email):
    registered = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "correct-horse-battery"},
    )
    assert registered.status_code == 201
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "correct-horse-battery"},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_project_create_list_retrieve_update(client):
    headers = register_and_login(client, "owner@example.com")
    created = client.post(
        "/api/v1/projects",
        headers=headers,
        json={"name": "  Support Assistant  ", "description": "Initial project"},
    )

    assert created.status_code == 201
    project = created.json()
    project_id = project["id"]
    assert project["name"] == "Support Assistant"
    assert project["description"] == "Initial project"
    assert UUID(project["owner_user_id"])

    listed = client.get("/api/v1/projects?offset=0&limit=10", headers=headers)
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [project_id]

    retrieved = client.get(f"/api/v1/projects/{project_id}", headers=headers)
    assert retrieved.status_code == 200
    assert retrieved.json() == project

    updated = client.patch(
        f"/api/v1/projects/{project_id}",
        headers=headers,
        json={"name": "Updated", "description": None},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Updated"
    assert updated.json()["description"] is None
    assert updated.json()["owner_user_id"] == project["owner_user_id"]


def test_project_create_derives_owner_and_rejects_reassignment(client):
    owner_headers = register_and_login(client, "owner@example.com")
    other_headers = register_and_login(client, "other@example.com")
    other_me = client.get("/api/v1/auth/me", headers=other_headers).json()

    created = client.post(
        "/api/v1/projects",
        headers=owner_headers,
        json={"name": "Owned", "owner_user_id": other_me["id"]},
    )
    assert created.status_code == 422

    created = client.post(
        "/api/v1/projects",
        headers=owner_headers,
        json={"name": "Owned"},
    )
    assert created.status_code == 201
    assert created.json()["owner_user_id"] != other_me["id"]

    patch = client.patch(
        f"/api/v1/projects/{created.json()['id']}",
        headers=owner_headers,
        json={"owner_user_id": other_me["id"]},
    )
    assert patch.status_code == 422


def test_projects_are_isolated_between_users(client):
    owner_headers = register_and_login(client, "owner@example.com")
    other_headers = register_and_login(client, "other@example.com")
    created = client.post(
        "/api/v1/projects",
        headers=owner_headers,
        json={"name": "Private"},
    )
    project_id = created.json()["id"]

    assert client.get("/api/v1/projects", headers=other_headers).json() == []
    assert client.get(f"/api/v1/projects/{project_id}", headers=other_headers).status_code == 404
    assert (
        client.patch(
            f"/api/v1/projects/{project_id}",
            headers=other_headers,
            json={"name": "Hijacked"},
        ).status_code
        == 404
    )


def test_project_routes_require_authentication_and_validate_pagination(client):
    assert client.get("/api/v1/projects").status_code == 401
    assert client.post("/api/v1/projects", json={"name": "Private"}).status_code == 401
    headers = register_and_login(client, "pagination@example.com")
    response = client.get("/api/v1/projects?limit=101", headers=headers)
    assert response.status_code == 422


def test_project_patch_preserves_unsupplied_fields(client):
    headers = register_and_login(client, "owner@example.com")
    created = client.post(
        "/api/v1/projects",
        headers=headers,
        json={"name": "Keep name", "description": "Keep description"},
    ).json()

    updated = client.patch(
        f"/api/v1/projects/{created['id']}",
        headers=headers,
        json={"description": "Changed"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Keep name"
    assert updated.json()["description"] == "Changed"


def test_empty_patch_is_rejected(client):
    headers = register_and_login(client, "owner@example.com")
    project = client.post(
        "/api/v1/projects",
        headers=headers,
        json={"name": "Project"},
    ).json()
    response = client.patch(
        f"/api/v1/projects/{project['id']}",
        headers=headers,
        json={},
    )
    assert response.status_code == 422
