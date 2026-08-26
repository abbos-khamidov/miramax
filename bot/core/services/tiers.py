import time
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import PointsTransaction, TierConfig

CACHE_TTL_SECONDS = 45

_cache: dict[int, int] | None = None
_cache_at: float = 0.0


def invalidate_cache() -> None:
    global _cache, _cache_at
    _cache = None
    _cache_at = 0.0


async def load_tiers(session: AsyncSession, force: bool = False) -> dict[int, int]:
    """{tier: points} for active tiers, ordered by tier — TTL-cached so a seller
    tapping amount buttons repeatedly doesn't hit the DB on every tap."""
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


async def record_tier_sale(
    session: AsyncSession,
    customer_id: int,
    store_id: int,
    seller_telegram_id: int,
    cart: dict[int, int],
) -> tuple[uuid.UUID, int]:
    """cart = {tier: qty}. One PointsTransaction row per unit — points frozen at the
    tier's current rate, not a reference to it. All rows share one sale_id and commit
    together (all-or-nothing, same guarantee a raw-SQL transaction would give)."""
    tiers = await load_tiers(session)
    sale_id = uuid.uuid4()
    total_points = 0

    for tier, qty in cart.items():
        points = tiers.get(tier, 0)
        for _ in range(qty):
            session.add(
                PointsTransaction(
                    customer_id=customer_id,
                    points=points,
                    amount=float(tier),
                    reason=f"{tier:,} сум".replace(",", " "),
                    store_id=store_id,
                    seller_telegram_id=seller_telegram_id,
                    tier=tier,
                    sale_id=sale_id,
                )
            )
            total_points += points

    await session.commit()
    return sale_id, total_points
