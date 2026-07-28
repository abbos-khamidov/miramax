"""admin-editable sum-to-points rate

Revision ID: 0007
Revises: 0006
Create Date: 2026-07-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "points_config",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sum_per_point", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.execute("INSERT INTO points_config (id, sum_per_point) VALUES (1, 20)")


def downgrade() -> None:
    op.drop_table("points_config")
