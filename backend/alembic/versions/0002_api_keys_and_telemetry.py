"""Add project API keys and canonical telemetry tables.

Revision ID: 0002_api_keys_telemetry
Revises: 0001_users_projects
Create Date: 2026-11-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0002_api_keys_telemetry"
down_revision: Union[str, None] = "0001_users_projects"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

json_object = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade() -> None:
    op.create_table(
        "api_keys",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("project_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("key_id", sa.String(length=32), nullable=False),
        sa.Column("prefix", sa.String(length=24), nullable=False),
        sa.Column("key_hash", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], name="fk_api_keys_project_id_projects"),
        sa.PrimaryKeyConstraint("id", name="pk_api_keys"),
        sa.UniqueConstraint("key_id", name="uq_api_keys_key_id"),
        sa.UniqueConstraint("key_hash", name="uq_api_keys_key_hash"),
    )
    op.create_index("ix_api_keys_project_id_created_at", "api_keys", ["project_id", "created_at"])

    op.create_table(
        "traces",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("project_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_ms", sa.BigInteger(), nullable=False),
        sa.Column("environment", sa.String(length=128), nullable=True),
        sa.Column("service_name", sa.String(length=128), nullable=True),
        sa.Column("attributes", json_object, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], name="fk_traces_project_id_projects"),
        sa.PrimaryKeyConstraint("id", name="pk_traces"),
        sa.UniqueConstraint("project_id", "id", name="uq_traces_project_id_id"),
        sa.CheckConstraint("duration_ms >= 0", name="ck_traces_duration_nonnegative"),
    )
    op.create_index("ix_traces_project_id_start_time", "traces", ["project_id", "start_time"])

    op.create_table(
        "spans",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("project_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("trace_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("parent_span_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("operation_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_ms", sa.BigInteger(), nullable=False),
        sa.Column("provider", sa.String(length=128), nullable=True),
        sa.Column("model", sa.String(length=255), nullable=True),
        sa.Column("input_tokens", sa.BigInteger(), nullable=True),
        sa.Column("output_tokens", sa.BigInteger(), nullable=True),
        sa.Column("total_tokens", sa.BigInteger(), nullable=True),
        sa.Column("estimated_cost", sa.Numeric(20, 10), nullable=True),
        sa.Column("estimated_cost_currency", sa.String(length=3), nullable=True),
        sa.Column("attributes", json_object, nullable=False),
        sa.Column("error_type", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id", "trace_id"],
            ["traces.project_id", "traces.id"],
            name="fk_spans_project_trace",
        ),
        sa.ForeignKeyConstraint(
            ["project_id", "trace_id", "parent_span_id"],
            ["spans.project_id", "spans.trace_id", "spans.id"],
            name="fk_spans_parent_same_trace",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_spans"),
        sa.UniqueConstraint("project_id", "trace_id", "id", name="uq_spans_project_trace_id_id"),
        sa.CheckConstraint("duration_ms >= 0", name="ck_spans_duration_nonnegative"),
        sa.CheckConstraint("input_tokens IS NULL OR input_tokens >= 0", name="ck_spans_input_tokens_nonnegative"),
        sa.CheckConstraint("output_tokens IS NULL OR output_tokens >= 0", name="ck_spans_output_tokens_nonnegative"),
        sa.CheckConstraint("total_tokens IS NULL OR total_tokens >= 0", name="ck_spans_total_tokens_nonnegative"),
        sa.CheckConstraint("estimated_cost IS NULL OR estimated_cost >= 0", name="ck_spans_estimated_cost_nonnegative"),
        sa.CheckConstraint(
            "(estimated_cost IS NULL AND estimated_cost_currency IS NULL) OR "
            "(estimated_cost IS NOT NULL AND estimated_cost_currency IS NOT NULL)",
            name="ck_spans_cost_currency_pair",
        ),
        sa.CheckConstraint("parent_span_id IS NULL OR parent_span_id != id", name="ck_spans_not_self_parent"),
    )
    op.create_index("ix_spans_project_id_trace_id", "spans", ["project_id", "trace_id"])
    op.create_index("ix_spans_project_id_parent_span_id", "spans", ["project_id", "parent_span_id"])

    op.create_table(
        "events",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("project_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("trace_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("span_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("attributes", json_object, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id", "trace_id"],
            ["traces.project_id", "traces.id"],
            name="fk_events_project_trace",
        ),
        sa.ForeignKeyConstraint(
            ["project_id", "trace_id", "span_id"],
            ["spans.project_id", "spans.trace_id", "spans.id"],
            name="fk_events_span_same_trace",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_events"),
    )
    op.create_index("ix_events_project_id_timestamp", "events", ["project_id", "timestamp"])
    op.create_index(
        "ix_events_project_id_trace_id_timestamp",
        "events",
        ["project_id", "trace_id", "timestamp"],
    )


def downgrade() -> None:
    op.drop_index("ix_events_project_id_trace_id_timestamp", table_name="events")
    op.drop_index("ix_events_project_id_timestamp", table_name="events")
    op.drop_table("events")
    op.drop_index("ix_spans_project_id_parent_span_id", table_name="spans")
    op.drop_index("ix_spans_project_id_trace_id", table_name="spans")
    op.drop_table("spans")
    op.drop_index("ix_traces_project_id_start_time", table_name="traces")
    op.drop_table("traces")
    op.drop_index("ix_api_keys_project_id_created_at", table_name="api_keys")
    op.drop_table("api_keys")
