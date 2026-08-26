"""invite codes: track who created each invite

Revision ID: 0006b
Revises: 0006
Create Date: 2026-07-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0006b"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("invite_codes", sa.Column("created_by_telegram_id", sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column("invite_codes", "created_by_telegram_id")
