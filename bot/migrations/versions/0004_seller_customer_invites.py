"""seller onboarding: customer phone + pending (invite-based) customer records

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("customer_cards", sa.Column("phone", sa.String(length=50), nullable=True))
    op.create_index("ix_customer_cards_phone", "customer_cards", ["phone"])
    op.alter_column("customer_cards", "telegram_id", nullable=True)

    op.execute("ALTER TYPE invite_target_role ADD VALUE IF NOT EXISTS 'customer'")

    op.add_column(
        "invite_codes", sa.Column("customer_card_id", sa.Integer(), sa.ForeignKey("customer_cards.id"), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("invite_codes", "customer_card_id")
    op.alter_column("customer_cards", "telegram_id", nullable=False)
    op.drop_index("ix_customer_cards_phone", table_name="customer_cards")
    op.drop_column("customer_cards", "phone")
