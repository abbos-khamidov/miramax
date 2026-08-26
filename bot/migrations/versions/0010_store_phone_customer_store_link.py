"""stores.phone + customer_cards.store_id (bind each customer to the store that registered them)

Revision ID: 0010
Revises: 0009
Create Date: 2026-08-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("stores", sa.Column("phone", sa.String(length=50), nullable=True))
    op.add_column("customer_cards", sa.Column("store_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_customer_cards_store_id_stores",
        "customer_cards",
        "stores",
        ["store_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_customer_cards_store_id_stores", "customer_cards", type_="foreignkey")
    op.drop_column("customer_cards", "store_id")
    op.drop_column("stores", "phone")
