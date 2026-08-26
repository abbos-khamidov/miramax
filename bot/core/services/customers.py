from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import CustomerCard, PointsConfig, PointsTransaction, Redemption, RedemptionStatus

DEFAULT_SUM_PER_POINT = 20  # fallback if the points_config row is somehow missing


async def create_pending_customer(session: AsyncSession, first_name: str, phone: str) -> CustomerCard:
    """A seller registers a customer who has never opened the customer bot yet —
    no telegram_id until they redeem the invite QR generated right after this."""
    customer = CustomerCard(full_name=first_name, phone=phone)
    session.add(customer)
    await session.commit()
    await session.refresh(customer)
    return customer


async def search_customers(session: AsyncSession, query: str, limit: int = 10) -> list[CustomerCard]:
    pattern = f"%{query}%"
    result = await session.execute(
        select(CustomerCard)
        .where(or_(CustomerCard.phone.ilike(pattern), CustomerCard.full_name.ilike(pattern)))
        .order_by(CustomerCard.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_customer(session: AsyncSession, customer_id: int) -> CustomerCard | None:
    return await session.get(CustomerCard, customer_id)


async def get_customer_balance(session: AsyncSession, customer_id: int) -> int:
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


async def get_sum_per_point(session: AsyncSession) -> int:
    config = await session.get(PointsConfig, 1)
    return config.sum_per_point if config else DEFAULT_SUM_PER_POINT


async def set_sum_per_point(session: AsyncSession, sum_per_point: int) -> None:
    config = await session.get(PointsConfig, 1)
    if config is None:
        config = PointsConfig(id=1, sum_per_point=sum_per_point)
        session.add(config)
    else:
        config.sum_per_point = sum_per_point
    await session.commit()


async def points_for_amount(session: AsyncSession, amount: float) -> int:
    sum_per_point = await get_sum_per_point(session)
    return round(amount / sum_per_point) if sum_per_point else 0


async def record_sale(
    session: AsyncSession,
    customer_id: int,
    store_id: int,
    seller_telegram_id: int,
    amount: float,
    product_name: str,
) -> PointsTransaction:
    points = await points_for_amount(session, amount)
    transaction = PointsTransaction(
        customer_id=customer_id,
        points=points,
        amount=amount,
        reason=product_name,
        store_id=store_id,
        seller_telegram_id=seller_telegram_id,
    )
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)
    return transaction
