"""expand ussd session_id length to 100

Revision ID: 20260304_01
Revises: 20260303_01
Create Date: 2026-03-04 08:45:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260304_01"
down_revision: Union[str, Sequence[str], None] = "20260303_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "ussd_session_events",
        "session_id",
        existing_type=sa.String(length=30),
        type_=sa.String(length=100),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "ussd_session_events",
        "session_id",
        existing_type=sa.String(length=100),
        type_=sa.String(length=30),
        existing_nullable=False,
    )

