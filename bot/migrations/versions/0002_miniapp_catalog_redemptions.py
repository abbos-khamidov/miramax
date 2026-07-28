"""miniapp catalog and redemptions

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE role_name ADD VALUE IF NOT EXISTS 'store'")
    op.execute("ALTER TYPE role_name ADD VALUE IF NOT EXISTS 'customer'")
    op.execute("ALTER TYPE role_name ADD VALUE IF NOT EXISTS 'admin'")

    redemption_status = postgresql.ENUM("pending", "fulfilled", "cancelled", name="redemption_status")
    redemption_status.create(op.get_bind(), checkfirst=True)
    redemption_status_column_type = postgresql.ENUM(
        "pending", "fulfilled", "cancelled", name="redemption_status", create_type=False
    )

    op.create_table(
        "customer_cards",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_unique_constraint("uq_customer_cards_telegram_id", "customer_cards", ["telegram_id"])
    op.create_index("ix_customer_cards_telegram_id", "customer_cards", ["telegram_id"])

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("category", sa.String(length=120), nullable=False),
        sa.Column("icon_or_image_url", sa.Text(), nullable=True),
        sa.Column("points_cost", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_products_category", "products", ["category"])
    op.create_index("ix_products_active", "products", ["active"])

    op.create_table(
        "points_transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customer_cards.id"), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("store_id", sa.Integer(), sa.ForeignKey("stores.id"), nullable=True),
        sa.Column("seller_telegram_id", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_points_transactions_customer_id", "points_transactions", ["customer_id"])

    op.create_table(
        "redemptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customer_cards.id"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column("points_spent", sa.Integer(), nullable=False),
        sa.Column("status", redemption_status_column_type, server_default="pending", nullable=False),
        sa.Column("confirmed_by", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_redemptions_customer_id", "redemptions", ["customer_id"])
    op.create_index("ix_redemptions_product_id", "redemptions", ["product_id"])
    op.create_index("ix_redemptions_status", "redemptions", ["status"])


def downgrade() -> None:
    op.drop_table("redemptions")
    op.drop_table("points_transactions")
    op.drop_table("products")
    op.drop_table("customer_cards")
    postgresql.ENUM(name="redemption_status").drop(op.get_bind(), checkfirst=True)
