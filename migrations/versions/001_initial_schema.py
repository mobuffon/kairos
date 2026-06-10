"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2025-06-08
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("telegram_username", sa.Text()),
        sa.Column("timezone", sa.Text(), nullable=False, server_default="UTC"),
        sa.Column("location_lat", sa.Float()),
        sa.Column("location_lng", sa.Float()),
        sa.Column("location_label", sa.Text()),
        sa.Column("quiet_hours_start", sa.Integer(), server_default="22"),
        sa.Column("quiet_hours_end", sa.Integer(), server_default="7"),
        sa.Column("max_suggestions_per_day", sa.Integer(), server_default="2"),
        sa.Column("check_in_frequency_days", sa.Integer(), server_default="14"),
        sa.Column("last_check_in_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "user_hobbies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("hobby_type", sa.Text(), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default="true"),
        sa.Column("config", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", "hobby_type"),
    )
    op.create_index("idx_user_hobbies_user_id", "user_hobbies", ["user_id"])

    op.create_table(
        "user_profile_facts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category", sa.Text(), nullable=False),
        sa.Column("fact", sa.Text(), nullable=False),
        sa.Column("valid_from", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("valid_until", sa.DateTime(timezone=True)),
        sa.Column("source", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_profile_facts_user_valid", "user_profile_facts", ["user_id", "valid_until"])

    op.create_table(
        "user_contacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("relationship_type", sa.Text()),
        sa.Column("contact_frequency_days", sa.Integer(), server_default="30"),
        sa.Column("last_contacted_at", sa.DateTime(timezone=True)),
        sa.Column("notes", sa.Text()),
    )
    op.create_index("idx_contacts_user_id", "user_contacts", ["user_id"])

    op.create_table(
        "user_calendars",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.Text(), server_default="google"),
        sa.Column("google_refresh_token", sa.Text()),
        sa.Column("calendar_id", sa.Text(), server_default="primary"),
        sa.Column("sync_enabled", sa.Boolean(), server_default="true"),
    )

    op.create_table(
        "suggestions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("hobby_type", sa.Text(), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("conditions_summary", sa.Text()),
        sa.Column("message_text", sa.Text()),
        sa.Column("sent_at", sa.DateTime(timezone=True)),
        sa.Column("response", sa.Text()),
        sa.Column("responded_at", sa.DateTime(timezone=True)),
        sa.Column("calendar_event_id", sa.Text()),
    )
    op.create_index("idx_suggestions_user_id_sent", "suggestions", ["user_id", "sent_at"])
    op.create_index("idx_suggestions_window", "suggestions", ["window_start", "window_end"])

    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("direction", sa.Text(), nullable=False),
        sa.Column("channel", sa.Text(), nullable=False),
        sa.Column("message_text", sa.Text(), nullable=False),
        sa.Column("extracted_facts", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_conversations_user_created", "conversations", ["user_id", "created_at"])


def downgrade() -> None:
    op.drop_index("idx_conversations_user_created", table_name="conversations")
    op.drop_table("conversations")
    op.drop_index("idx_suggestions_window", table_name="suggestions")
    op.drop_index("idx_suggestions_user_id_sent", table_name="suggestions")
    op.drop_table("suggestions")
    op.drop_table("user_calendars")
    op.drop_index("idx_contacts_user_id", table_name="user_contacts")
    op.drop_table("user_contacts")
    op.drop_index("idx_profile_facts_user_valid", table_name="user_profile_facts")
    op.drop_table("user_profile_facts")
    op.drop_index("idx_user_hobbies_user_id", table_name="user_hobbies")
    op.drop_table("user_hobbies")
    op.drop_table("users")
