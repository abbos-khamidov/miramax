from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from services.backend.deps import Principal, TelegramUser, get_db, get_telegram_user, require_admin, require_factory
from core.models import CustomerCard, PointsTransaction, Product, Redemption, RedemptionStatus, Role, RoleName
from core.schemas import (
    MiniAppMe,
    ProductCreate,
    ProductOut,
    ProductUpdate,
    RedemptionCreate,
    RedemptionCreateOut,
    RedemptionOut,
)

router = APIRouter(prefix="/api", tags=["miniapp"])


async def _get_or_create_customer(session: AsyncSession, user: TelegramUser) -> CustomerCard:
    result = await session.execute(select(CustomerCard).where(CustomerCard.telegram_id == user.telegram_id))
    customer = result.scalar_one_or_none()
    full_name = " ".join(part for part in [user.first_name, user.last_name] if part) or user.username

    if customer is None:
        customer = CustomerCard(telegram_id=user.telegram_id, full_name=full_name)
        session.add(customer)
        await session.flush()
    elif full_name and customer.full_name != full_name:
        customer.full_name = full_name
        await session.flush()

    return customer


async def _customer_balance(session: AsyncSession, customer_id: int) -> int:
    earned_result = await session.execute(
        select(func.coalesce(func.sum(PointsTransaction.points), 0)).where(
            PointsTransaction.customer_id == customer_id
        )
    )
    fulfilled_result = await session.execute(
        select(func.coalesce(func.sum(Redemption.points_spent), 0)).where(
            Redemption.customer_id == customer_id,
            Redemption.status == RedemptionStatus.FULFILLED,
        )
    )
    return int(earned_result.scalar_one() or 0) - int(fulfilled_result.scalar_one() or 0)


async def _is_admin(session: AsyncSession, telegram_id: int) -> bool:
    result = await session.execute(select(Role).where(Role.telegram_id == telegram_id, Role.role == RoleName.ADMIN))
    return result.scalar_one_or_none() is not None


def _redemption_out(redemption: Redemption) -> RedemptionOut:
    return RedemptionOut(
        id=redemption.id,
        customer_id=redemption.customer_id,
        product_id=redemption.product_id,
        product_name=redemption.product.name,
        product_category=redemption.product.category,
        product_icon_or_image_url=redemption.product.icon_or_image_url,
        qty=redemption.qty,
        points_spent=redemption.points_spent,
        status=redemption.status.value,
        confirmed_by=redemption.confirmed_by,
        created_at=redemption.created_at,
        confirmed_at=redemption.confirmed_at,
    )


@router.get("/miniapp/me", response_model=MiniAppMe)
async def miniapp_me(
    session: AsyncSession = Depends(get_db),
    user: TelegramUser = Depends(get_telegram_user),
) -> MiniAppMe:
    customer = await _get_or_create_customer(session, user)
    balance = await _customer_balance(session, customer.id)
    is_admin = await _is_admin(session, user.telegram_id)
    await session.commit()
    return MiniAppMe(
        customer_id=customer.id,
        telegram_id=customer.telegram_id,
        full_name=customer.full_name,
        balance=balance,
        is_admin=is_admin,
    )


@router.get("/miniapp/products", response_model=list[ProductOut])
async def list_active_products(
    category: str | None = None,
    session: AsyncSession = Depends(get_db),
) -> list[ProductOut]:
    stmt = select(Product).where(Product.active.is_(True)).order_by(Product.category, Product.name)
    if category:
        stmt = stmt.where(Product.category == category)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.post("/miniapp/redemptions", response_model=RedemptionCreateOut, status_code=status.HTTP_201_CREATED)
async def create_redemptions(
    payload: RedemptionCreate,
    session: AsyncSession = Depends(get_db),
    user: TelegramUser = Depends(get_telegram_user),
) -> RedemptionCreateOut:
    items = [item for item in payload.items if item.qty > 0]
    if not items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="savatcha bo'sh")

    customer = await _get_or_create_customer(session, user)
    product_ids = {item.product_id for item in items}
    products_result = await session.execute(
        select(Product).where(Product.id.in_(product_ids), Product.active.is_(True))
    )
    products = {product.id: product for product in products_result.scalars().all()}
    if len(products) != len(product_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="mahsulot topilmadi yoki faol emas")

    total_points = sum(products[item.product_id].points_cost * item.qty for item in items)
    balance = await _customer_balance(session, customer.id)
    if total_points > balance:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ball yetarli emas")

    redemptions: list[Redemption] = []
    for item in items:
        product = products[item.product_id]
        redemption = Redemption(
            customer_id=customer.id,
            product_id=product.id,
            qty=item.qty,
            points_spent=product.points_cost * item.qty,
            status=RedemptionStatus.PENDING,
        )
        session.add(redemption)
        redemptions.append(redemption)

    await session.commit()
    for redemption in redemptions:
        await session.refresh(redemption, attribute_names=["product"])

    return RedemptionCreateOut(items=[_redemption_out(item) for item in redemptions], total_points=total_points)


@router.get("/miniapp/redemptions/me", response_model=list[RedemptionOut])
async def list_my_redemptions(
    session: AsyncSession = Depends(get_db),
    user: TelegramUser = Depends(get_telegram_user),
) -> list[RedemptionOut]:
    customer = await _get_or_create_customer(session, user)
    result = await session.execute(
        select(Redemption)
        .options(selectinload(Redemption.product))
        .where(Redemption.customer_id == customer.id)
        .order_by(Redemption.created_at.desc())
    )
    return [_redemption_out(redemption) for redemption in result.scalars().all()]


@router.get("/admin/products", response_model=list[ProductOut])
async def admin_list_products(
    session: AsyncSession = Depends(get_db),
    _principal: Principal = Depends(require_factory),
) -> list[ProductOut]:
    result = await session.execute(select(Product).order_by(Product.created_at.desc(), Product.id.desc()))
    return list(result.scalars().all())


@router.post("/admin/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def admin_create_product(
    payload: ProductCreate,
    session: AsyncSession = Depends(get_db),
    _principal: Principal = Depends(require_admin),
) -> ProductOut:
    if payload.points_cost <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ball narxi musbat bo'lishi kerak")
    product = Product(**payload.model_dump())
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


@router.put("/admin/products/{product_id}", response_model=ProductOut)
async def admin_update_product(
    product_id: int,
    payload: ProductUpdate,
    session: AsyncSession = Depends(get_db),
    _principal: Principal = Depends(require_admin),
) -> ProductOut:
    result = await session.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="mahsulot topilmadi")

    update_data = payload.model_dump(exclude_unset=True)
    if "points_cost" in update_data and update_data["points_cost"] <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ball narxi musbat bo'lishi kerak")
    for field, value in update_data.items():
        setattr(product, field, value)

    await session.commit()
    await session.refresh(product)
    return product


@router.delete("/admin/products/{product_id}", response_model=ProductOut)
async def admin_hide_product(
    product_id: int,
    session: AsyncSession = Depends(get_db),
    _principal: Principal = Depends(require_admin),
) -> ProductOut:
    result = await session.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="mahsulot topilmadi")
    product.active = False
    await session.commit()
    await session.refresh(product)
    return product


@router.get("/admin/redemptions", response_model=list[RedemptionOut])
async def admin_list_redemptions(
    redemption_status: RedemptionStatus | None = Query(None, alias="status"),
    session: AsyncSession = Depends(get_db),
    _principal: Principal = Depends(require_admin),
) -> list[RedemptionOut]:
    stmt = select(Redemption).options(selectinload(Redemption.product)).order_by(Redemption.created_at.desc())
    if redemption_status is not None:
        stmt = stmt.where(Redemption.status == redemption_status)
    result = await session.execute(stmt)
    return [_redemption_out(redemption) for redemption in result.scalars().all()]


@router.post("/admin/redemptions/{redemption_id}/confirm", response_model=RedemptionOut)
async def admin_confirm_redemption(
    redemption_id: int,
    session: AsyncSession = Depends(get_db),
    principal: Principal = Depends(require_admin),
) -> RedemptionOut:
    result = await session.execute(
        select(Redemption).options(selectinload(Redemption.product)).where(Redemption.id == redemption_id)
    )
    redemption = result.scalar_one_or_none()
    if redemption is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="so'rov topilmadi")
    if redemption.status != RedemptionStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="faqat kutilayotgan so'rov tasdiqlanadi")

    balance = await _customer_balance(session, redemption.customer_id)
    if redemption.points_spent > balance:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="mijoz balansi yetarli emas")

    redemption.status = RedemptionStatus.FULFILLED
    redemption.confirmed_by = principal.telegram_id
    redemption.confirmed_at = datetime.utcnow()
    await session.commit()
    await session.refresh(redemption, attribute_names=["product"])
    return _redemption_out(redemption)


@router.post("/admin/redemptions/{redemption_id}/cancel", response_model=RedemptionOut)
async def admin_cancel_redemption(
    redemption_id: int,
    session: AsyncSession = Depends(get_db),
    principal: Principal = Depends(require_admin),
) -> RedemptionOut:
    result = await session.execute(
        select(Redemption).options(selectinload(Redemption.product)).where(Redemption.id == redemption_id)
    )
    redemption = result.scalar_one_or_none()
    if redemption is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="so'rov topilmadi")
    if redemption.status != RedemptionStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="faqat kutilayotgan so'rov bekor qilinadi")

    redemption.status = RedemptionStatus.CANCELLED
    redemption.confirmed_by = principal.telegram_id
    redemption.confirmed_at = datetime.utcnow()
    await session.commit()
    await session.refresh(redemption, attribute_names=["product"])
    return _redemption_out(redemption)
