"""seller_bot amount buttons: tier_config table + tier/sale_id on points_transactions

Revision ID: 0009
Revises: 0008
Create Date: 2026-08-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tier_config",
        sa.Column("tier", sa.Integer(), primary_key=True),
        sa.Column("points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.bulk_insert(
        sa.table(
            "tier_config",
            sa.column("tier", sa.Integer()),
            sa.column("points", sa.Integer()),
        ),
        [
            {"tier": 300000, "points": 0},
            {"tier": 500000, "points": 0},
            {"tier": 1000000, "points": 0},
            {"tier": 5000000, "points": 0},
            {"tier": 10000000, "points": 0},
        ],
    )

    op.add_column("points_transactions", sa.Column("tier", sa.Integer(), nullable=True))
    op.add_column(
        "points_transactions", sa.Column("sale_id", postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.create_index("ix_points_transactions_sale_id", "points_transactions", ["sale_id"])


def downgrade() -> None:
    op.drop_index("ix_points_transactions_sale_id", table_name="points_transactions")
    op.drop_column("points_transactions", "sale_id")
    op.drop_column("points_transactions", "tier")
    op.drop_table("tier_config")
