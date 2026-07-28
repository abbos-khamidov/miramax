"""per-customer language preference

Revision ID: 0006
Revises: 0005
Create Date: 2026-07-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("customer_cards", sa.Column("language", sa.String(length=5), nullable=True))


def downgrade() -> None:
    op.drop_column("customer_cards", "language")
