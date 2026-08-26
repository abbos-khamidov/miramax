"""track the raw sale amount per points_transactions row (for the analytics page)

Revision ID: 0008
Revises: 0007
Create Date: 2026-08-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("points_transactions", sa.Column("amount", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("points_transactions", "amount")
