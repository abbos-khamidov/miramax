import time
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import PointsTransaction, TierConfig
from core.services import customers as customers_service

CACHE_TTL_SECONDS = 45

_cache: dict[int, int] | None = None
_cache_at: float = 0.0


def invalidate_cache() -> None:
    global _cache, _cache_at
    _cache = None
    _cache_at = 0.0


async def load_tiers(session: AsyncSession, force: bool = False) -> dict[int, int]:
    """{tier: points} for active tiers, ordered by tier — TTL-cached so a seller
    tapping amount buttons repeatedly doesn't hit the DB on every tap.

    The `points` value is legacy/informational only — since the sum→points switch to
    a single global rate (customers_service.points_for_amount, "Курс баллов" in
    admin_bot), actual awarding is computed off the whole sale's total amount, not
    per-tier. Callers only need this dict's keys (the номинал amounts) for buttons."""
    global _cache, _cache_at
    if not force and _cache is not None and (time.monotonic() - _cache_at) < CACHE_TTL_SECONDS:
        return _cache

    result = await session.execute(
        select(TierConfig).where(TierConfig.active.is_(True)).order_by(TierConfig.tier)
    )
    tiers = {row.tier: row.points for row in result.scalars().all()}
    _cache, _cache_at = tiers, time.monotonic()
    return tiers


async def list_tiers(session: AsyncSession) -> list[TierConfig]:
    result = await session.execute(select(TierConfig).order_by(TierConfig.tier))
    return list(result.scalars().all())


class TierNotFoundError(Exception):
    pass


async def set_tier_points(session: AsyncSession, tier: int, points: int) -> TierConfig:
    config = await session.get(TierConfig, tier)
    if config is None:
        raise TierNotFoundError(tier)
    config.points = points
    await session.commit()
    invalidate_cache()
    return config


def total_amount_for_cart(cart: dict[int, int]) -> int:
    return sum(tier * qty for tier, qty in cart.items())


async def points_for_cart(session: AsyncSession, cart: dict[int, int]) -> int:
    """Points for the whole sale (all tapped номинал buttons combined), off the
    single global rate — not summed from per-tier fractions. Tapping 300 000 +
    500 000 (800 000 total) at a 1 000 000=1 rate rounds once, at the end, same as
    a single 800 000 purchase would — never per-button, or a seller could split one
    sale across several sub-1-point taps and lose the customer's points to rounding."""
    return await customers_service.points_for_amount(session, total_amount_for_cart(cart))


async def record_tier_sale(
    session: AsyncSession,
    customer_id: int,
    store_id: int,
    seller_telegram_id: int,
    cart: dict[int, int],
) -> tuple[uuid.UUID, int]:
    """cart = {tier: qty}. One PointsTransaction row for the whole sale — points are
    computed once off the total amount (see points_for_cart), not per tapped button."""
    total_amount = total_amount_for_cart(cart)
    total_points = await customers_service.points_for_amount(session, total_amount)
    sale_id = uuid.uuid4()

    breakdown = ", ".join(
        f"{tier:,}".replace(",", " ") + (f"×{qty}" if qty > 1 else "") for tier, qty in sorted(cart.items())
    )
    session.add(
        PointsTransaction(
            customer_id=customer_id,
            points=total_points,
            amount=float(total_amount),
            reason=breakdown,
            store_id=store_id,
            seller_telegram_id=seller_telegram_id,
            tier=None,
            sale_id=sale_id,
        )
    )

    await session.commit()
    return sale_id, total_points
