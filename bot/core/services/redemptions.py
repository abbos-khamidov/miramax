from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.models import Product, Redemption, RedemptionStatus
from core.services import customers as customers_service


class RedemptionNotPendingError(Exception):
    pass


class ProductNotFoundError(Exception):
    pass


class InsufficientBalanceError(Exception):
    def __init__(self, needed: int, balance: int):
        self.needed = needed
        self.balance = balance


async def list_pending_for_customer(session: AsyncSession, customer_id: int) -> list[Redemption]:
    result = await session.execute(
        select(Redemption)
        .options(selectinload(Redemption.product))
        .where(Redemption.customer_id == customer_id, Redemption.status == RedemptionStatus.PENDING)
        .order_by(Redemption.created_at)
    )
    return list(result.scalars().all())


async def get_redemption(session: AsyncSession, redemption_id: int) -> Redemption | None:
    result = await session.execute(
        select(Redemption).options(selectinload(Redemption.product)).where(Redemption.id == redemption_id)
    )
    return result.scalar_one_or_none()


async def create_redemption(session: AsyncSession, customer_id: int, product_id: int, qty: int = 1) -> Redemption:
    product = await session.get(Product, product_id)
    if product is None or not product.active:
        raise ProductNotFoundError(product_id)

    points_spent = product.points_cost * qty
    balance = await customers_service.get_customer_balance(session, customer_id)
    if points_spent > balance:
        raise InsufficientBalanceError(needed=points_spent, balance=balance)

    redemption = Redemption(
        customer_id=customer_id,
        product_id=product_id,
        qty=qty,
        points_spent=points_spent,
        status=RedemptionStatus.PENDING,
    )
    session.add(redemption)
    await session.commit()
    await session.refresh(redemption, attribute_names=["product"])
    return redemption


async def fulfill_redemption(session: AsyncSession, redemption_id: int, confirmed_by_telegram_id: int) -> Redemption:
    redemption = await get_redemption(session, redemption_id)
    if redemption is None or redemption.status != RedemptionStatus.PENDING:
        raise RedemptionNotPendingError(redemption_id)

    balance = await customers_service.get_customer_balance(session, redemption.customer_id)
    if redemption.points_spent > balance:
        raise InsufficientBalanceError(needed=redemption.points_spent, balance=balance)

    redemption.status = RedemptionStatus.FULFILLED
    redemption.confirmed_by = confirmed_by_telegram_id
    redemption.confirmed_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(redemption)
    return redemption
