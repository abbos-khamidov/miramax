import enum
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base


class RoleName(str, enum.Enum):
    FACTORY = "factory"
    SUPPLIER = "supplier"
    STORE = "store"
    SELLER = "seller"
    CUSTOMER = "customer"
    ADMIN = "admin"


class RedemptionStatus(str, enum.Enum):
    PENDING = "pending"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"


class SupplierKind(str, enum.Enum):
    SUPPLIER = "supplier"
    WHOLESALER = "wholesaler"


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    kind: Mapped[SupplierKind] = mapped_column(
        Enum(SupplierKind, name="supplier_kind", values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        default=SupplierKind.SUPPLIER,
        server_default=SupplierKind.SUPPLIER.value,
    )
    contact_first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    stores: Mapped[list["Store"]] = relationship(back_populates="supplier")


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"))
    name: Mapped[str] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    supplier: Mapped["Supplier"] = relationship(back_populates="stores")
    invite_codes: Mapped[list["InviteCode"]] = relationship(back_populates="store")


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    role: Mapped[RoleName] = mapped_column(
        Enum(RoleName, name="role_name", values_callable=lambda enum_cls: [e.value for e in enum_cls])
    )
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"), nullable=True)
    store_id: Mapped[int | None] = mapped_column(ForeignKey("stores.id"), nullable=True)
    language: Mapped[str | None] = mapped_column(String(5), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CustomerCard(Base):
    __tablename__ = "customer_cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, index=True, nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), index=True, nullable=True)
    language: Mapped[str | None] = mapped_column(String(5), nullable=True)
    store_id: Mapped[int | None] = mapped_column(ForeignKey("stores.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    points_transactions: Mapped[list["PointsTransaction"]] = relationship(back_populates="customer")
    redemptions: Mapped[list["Redemption"]] = relationship(back_populates="customer")


class PointsTransaction(Base):
    __tablename__ = "points_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer_cards.id"), index=True)
    points: Mapped[int] = mapped_column(Integer)
    amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    store_id: Mapped[int | None] = mapped_column(ForeignKey("stores.id"), nullable=True)
    seller_telegram_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    tier: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sale_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    customer: Mapped["CustomerCard"] = relationship(back_populates="points_transactions")


class TierConfig(Base):
    """One row per fixed sale-amount button (номинал) shown in seller_bot's amount
    composer. `points` is Factory/Admin-editable via /set_tier; new sales freeze the
    current value into PointsTransaction.points — past rows are never recalculated."""

    __tablename__ = "tier_config"

    tier: Mapped[int] = mapped_column(Integer, primary_key=True)
    points: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")


class PointsConfig(Base):
    """Single-row table (id is always 1) holding the network-wide sum-to-points rate,
    editable by Factory/Admin — new purchases read the current row live, past
    PointsTransaction rows are never recalculated."""

    __tablename__ = "points_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    sum_per_point: Mapped[int] = mapped_column(Integer, default=20, server_default="20")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(120), index=True)
    icon_or_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    points_cost: Mapped[int] = mapped_column(Integer)
    active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    redemptions: Mapped[list["Redemption"]] = relationship(back_populates="product")


class Redemption(Base):
    __tablename__ = "redemptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer_cards.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    qty: Mapped[int] = mapped_column(Integer)
    points_spent: Mapped[int] = mapped_column(Integer)
    status: Mapped[RedemptionStatus] = mapped_column(
        Enum(
            RedemptionStatus,
            name="redemption_status",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        default=RedemptionStatus.PENDING,
        server_default=RedemptionStatus.PENDING.value,
        index=True,
    )
    confirmed_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    customer: Mapped["CustomerCard"] = relationship(back_populates="redemptions")
    product: Mapped["Product"] = relationship(back_populates="redemptions")


class InviteTargetRole(str, enum.Enum):
    SUPPLIER = "supplier"
    SELLER = "seller"
    CUSTOMER = "customer"
    ADMIN = "admin"


class InviteCode(Base):
    __tablename__ = "invite_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    target_role: Mapped[InviteTargetRole] = mapped_column(
        Enum(
            InviteTargetRole,
            name="invite_target_role",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        default=InviteTargetRole.SELLER,
        server_default=InviteTargetRole.SELLER.value,
    )
    store_id: Mapped[int | None] = mapped_column(ForeignKey("stores.id"), nullable=True)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"), nullable=True)
    customer_card_id: Mapped[int | None] = mapped_column(ForeignKey("customer_cards.id"), nullable=True)
    contact_first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_by_telegram_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    used_by_telegram_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    store: Mapped["Store | None"] = relationship(back_populates="invite_codes")
