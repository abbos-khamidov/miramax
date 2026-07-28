from datetime import datetime

from pydantic import BaseModel


class StoreCreate(BaseModel):
    supplier_id: int
    name: str
    address: str | None = None
    city: str | None = None


class StoreUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    city: str | None = None


class StoreOut(BaseModel):
    id: int
    supplier_id: int
    name: str
    address: str | None
    city: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class InviteSellerIn(BaseModel):
    first_name: str
    last_name: str


class InviteOut(BaseModel):
    code: str
    link: str


class SupplierCreateIn(BaseModel):
    first_name: str
    last_name: str
    phone: str
    company_name: str
    city: str | None = None
    kind: str = "supplier"


class SupplierInviteOut(BaseModel):
    supplier_id: int
    supplier_name: str
    kind: str
    code: str
    link: str


class AdminCreateIn(BaseModel):
    first_name: str
    last_name: str
    phone: str


class AdminInviteOut(BaseModel):
    code: str
    link: str


class StoreAnalytics(BaseModel):
    store_id: int
    store_name: str
    total_sales: int = 0
    total_points_issued: int = 0
    last_sale_at: datetime | None = None


class SupplierAnalytics(BaseModel):
    supplier_id: int
    supplier_name: str
    store_count: int
    stores: list[StoreAnalytics]


class FactoryAnalytics(BaseModel):
    supplier_count: int
    store_count: int
    suppliers: list[SupplierAnalytics]


class AdminListItem(BaseModel):
    telegram_id: int
    first_name: str | None
    last_name: str | None
    phone: str | None


class SupplierListItem(BaseModel):
    id: int
    name: str
    kind: str
    city: str | None
    contact_first_name: str | None
    contact_last_name: str | None
    contact_phone: str | None
    store_count: int
    total_purchases: int
    total_points_issued: int
    created_at: datetime


class SupplierDetail(BaseModel):
    id: int
    name: str
    kind: str
    city: str | None
    contact_first_name: str | None
    contact_last_name: str | None
    contact_phone: str | None
    created_at: datetime
    total_purchases: int
    total_points_issued: int
    stores: list[StoreAnalytics]


class OverviewTotals(BaseModel):
    supplier_count: int
    wholesaler_count: int
    store_count: int
    total_purchases: int
    total_points_issued: int


class OverviewSeriesPoint(BaseModel):
    date: str
    purchases: int
    points_issued: int


class OverviewKindBreakdown(BaseModel):
    kind: str
    purchases: int
    points_issued: int
    entity_count: int


class OverviewTopEntity(BaseModel):
    id: int
    name: str
    kind: str
    store_count: int
    total_purchases: int
    total_points_issued: int


class FactoryOverview(BaseModel):
    totals: OverviewTotals
    series: list[OverviewSeriesPoint]
    by_kind: list[OverviewKindBreakdown]
    top: list[OverviewTopEntity]


class MiniAppMe(BaseModel):
    customer_id: int
    telegram_id: int
    full_name: str | None
    balance: int
    is_admin: bool = False


class ProductBase(BaseModel):
    name: str
    category: str
    icon_or_image_url: str | None = None
    points_cost: int
    active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    icon_or_image_url: str | None = None
    points_cost: int | None = None
    active: bool | None = None


class ProductOut(ProductBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class RedemptionItemIn(BaseModel):
    product_id: int
    qty: int


class RedemptionCreate(BaseModel):
    items: list[RedemptionItemIn]


class RedemptionOut(BaseModel):
    id: int
    customer_id: int
    product_id: int
    product_name: str
    product_category: str
    product_icon_or_image_url: str | None
    qty: int
    points_spent: int
    status: str
    confirmed_by: int | None
    created_at: datetime
    confirmed_at: datetime | None


class RedemptionCreateOut(BaseModel):
    items: list[RedemptionOut]
    total_points: int
