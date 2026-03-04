"""create orders and ussd_session_events tables

Revision ID: 20260303_01
Revises:
Create Date: 2026-03-03 11:55:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260303_01"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


item_code_enum = postgresql.ENUM(
    "BURGER", "CHIPS", "SODA", name="itemcode", create_type=False
)
order_status_enum = postgresql.ENUM(
    "PENDING", "STK_SENT", "PAID", "FAILED", name="orderstatus", create_type=False
)


def upgrade() -> None:
    bind = op.get_bind()
    item_code_enum.create(bind, checkfirst=True)
    order_status_enum.create(bind, checkfirst=True)

    op.create_table(
        "orders",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("session_id", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("item_code", item_code_enum, nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            order_status_enum,
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("provider_ref", sa.String(length=120), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_orders_session_id", "orders", ["session_id"], unique=False)
    op.create_index("ix_orders_phone", "orders", ["phone"], unique=False)
    op.create_index("ix_orders_status", "orders", ["status"], unique=False)
    op.create_index(
        "ix_orders_provider_ref", "orders", ["provider_ref"], unique=False
    )

    op.create_table(
        "ussd_session_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("session_id", sa.String(length=30), nullable=False),
        sa.Column("service_code", sa.String(length=30), nullable=False),
        sa.Column("network_code", sa.String(length=10), nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=False),
        sa.Column("date_utc", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("cost", sa.String(length=20), nullable=False),
        sa.Column("duration_in_millis", sa.String(length=20), nullable=False),
        sa.Column("hops_count", sa.Integer(), nullable=False),
        sa.Column("input", sa.Text(), nullable=False),
        sa.Column("last_app_response", sa.Text(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_ussd_session_events_session_id",
        "ussd_session_events",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        "ix_ussd_session_events_phone_number",
        "ussd_session_events",
        ["phone_number"],
        unique=False,
    )
    op.create_index(
        "ix_ussd_session_events_status",
        "ussd_session_events",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_ussd_session_events_status", table_name="ussd_session_events")
    op.drop_index(
        "ix_ussd_session_events_phone_number", table_name="ussd_session_events"
    )
    op.drop_index("ix_ussd_session_events_session_id", table_name="ussd_session_events")
    op.drop_table("ussd_session_events")

    op.drop_index("ix_orders_provider_ref", table_name="orders")
    op.drop_index("ix_orders_status", table_name="orders")
    op.drop_index("ix_orders_phone", table_name="orders")
    op.drop_index("ix_orders_session_id", table_name="orders")
    op.drop_table("orders")

    bind = op.get_bind()
    order_status_enum.drop(bind, checkfirst=True)
    item_code_enum.drop(bind, checkfirst=True)
