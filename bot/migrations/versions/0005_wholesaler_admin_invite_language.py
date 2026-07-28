"""supplier kind + city (supplier/wholesaler), admin invite target role, per-role language pref

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    supplier_kind = postgresql.ENUM("supplier", "wholesaler", name="supplier_kind")
    supplier_kind.create(op.get_bind(), checkfirst=True)
    supplier_kind_column_type = postgresql.ENUM("supplier", "wholesaler", name="supplier_kind", create_type=False)
    op.add_column(
        "suppliers",
        sa.Column("kind", supplier_kind_column_type, server_default="supplier", nullable=False),
    )
    op.add_column("suppliers", sa.Column("city", sa.String(length=255), nullable=True))

    op.execute("ALTER TYPE invite_target_role ADD VALUE IF NOT EXISTS 'admin'")

    op.add_column("roles", sa.Column("language", sa.String(length=5), nullable=True))


def downgrade() -> None:
    op.drop_column("roles", "language")

    op.drop_column("suppliers", "city")
    op.drop_column("suppliers", "kind")
    postgresql.ENUM(name="supplier_kind").drop(op.get_bind(), checkfirst=True)

    # Postgres can't drop a single enum value; 'admin' stays in invite_target_role on downgrade.
