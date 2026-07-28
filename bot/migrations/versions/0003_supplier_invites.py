"""supplier contact fields + generalized invite codes (supplier or seller)

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("suppliers", sa.Column("contact_first_name", sa.String(length=255), nullable=True))
    op.add_column("suppliers", sa.Column("contact_last_name", sa.String(length=255), nullable=True))
    op.add_column("suppliers", sa.Column("contact_phone", sa.String(length=50), nullable=True))

    invite_target_role = postgresql.ENUM("supplier", "seller", name="invite_target_role")
    invite_target_role.create(op.get_bind(), checkfirst=True)
    invite_target_role_column_type = postgresql.ENUM(
        "supplier", "seller", name="invite_target_role", create_type=False
    )

    op.add_column(
        "invite_codes",
        sa.Column(
            "target_role", invite_target_role_column_type, server_default="seller", nullable=False
        ),
    )
    op.add_column("invite_codes", sa.Column("supplier_id", sa.Integer(), sa.ForeignKey("suppliers.id"), nullable=True))
    op.add_column("invite_codes", sa.Column("contact_first_name", sa.String(length=255), nullable=True))
    op.add_column("invite_codes", sa.Column("contact_last_name", sa.String(length=255), nullable=True))
    op.add_column("invite_codes", sa.Column("contact_phone", sa.String(length=50), nullable=True))
    op.alter_column("invite_codes", "store_id", nullable=True)


def downgrade() -> None:
    op.alter_column("invite_codes", "store_id", nullable=False)
    op.drop_column("invite_codes", "contact_phone")
    op.drop_column("invite_codes", "contact_last_name")
    op.drop_column("invite_codes", "contact_first_name")
    op.drop_column("invite_codes", "supplier_id")
    op.drop_column("invite_codes", "target_role")
    postgresql.ENUM(name="invite_target_role").drop(op.get_bind(), checkfirst=True)

    op.drop_column("suppliers", "contact_phone")
    op.drop_column("suppliers", "contact_last_name")
    op.drop_column("suppliers", "contact_first_name")
