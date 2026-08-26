from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.models import PointsTransaction, Store, Supplier, SupplierKind
from core.schemas import (
    FactoryAnalytics,
    FactoryOverview,
    OverviewKindBreakdown,
    OverviewSeriesPoint,
    OverviewTopEntity,
    OverviewTotals,
    SellerLeaderboardItem,
    StoreAnalytics,
    StoreLeaderboardItem,
    SupplierAnalytics,
    WebHomeOut,
    WebHomeTotals,
)
from core.services import directory as directory_service

StoreStats = dict[int, tuple[int, int, datetime | None]]


async def _store_stats_map(session: AsyncSession, store_ids: list[int]) -> StoreStats:
    if not store_ids:
        return {}
    result = await session.execute(
        select(
            PointsTransaction.store_id,
            func.count(PointsTransaction.id),
            func.coalesce(func.sum(PointsTransaction.points), 0),
            func.max(PointsTransaction.created_at),
        )
        .where(PointsTransaction.store_id.in_(store_ids))
        .group_by(PointsTransaction.store_id)
    )
    return {row[0]: (int(row[1]), int(row[2]), row[3]) for row in result.all()}


def _store_analytics(store: Store, stats: StoreStats) -> StoreAnalytics:
    count, points, last_sale_at = stats.get(store.id, (0, 0, None))
    return StoreAnalytics(
        store_id=store.id,
        store_name=store.name,
        total_sales=count,
        total_points_issued=points,
        last_sale_at=last_sale_at,
    )


def _supplier_analytics(supplier: Supplier, stats: StoreStats) -> SupplierAnalytics:
    stores = [_store_analytics(s, stats) for s in supplier.stores]
    return SupplierAnalytics(
        supplier_id=supplier.id,
        supplier_name=supplier.name,
        store_count=len(stores),
        stores=stores,
    )


async def get_factory_analytics(
    session: AsyncSession, supplier_id: int | None = None, store_id: int | None = None
) -> FactoryAnalytics:
    query = select(Supplier).options(selectinload(Supplier.stores))
    if supplier_id is not None:
        query = query.where(Supplier.id == supplier_id)
    result = await session.execute(query)
    suppliers = list(result.scalars().all())

    all_store_ids = [s.id for supplier in suppliers for s in supplier.stores]
    stats = await _store_stats_map(session, all_store_ids)

    supplier_analytics = [_supplier_analytics(s, stats) for s in suppliers]
    if store_id is not None:
        for sa in supplier_analytics:
            sa.stores = [st for st in sa.stores if st.store_id == store_id]
            sa.store_count = len(sa.stores)

    return FactoryAnalytics(
        supplier_count=len(supplier_analytics),
        store_count=sum(sa.store_count for sa in supplier_analytics),
        suppliers=supplier_analytics,
    )


async def get_supplier_analytics(session: AsyncSession, supplier_id: int) -> SupplierAnalytics | None:
    query = select(Supplier).options(selectinload(Supplier.stores)).where(Supplier.id == supplier_id)
    result = await session.execute(query)
    supplier = result.scalar_one_or_none()
    if supplier is None:
        return None
    stats = await _store_stats_map(session, [s.id for s in supplier.stores])
    return _supplier_analytics(supplier, stats)


async def get_supplier_purchase_stats(session: AsyncSession, supplier_id: int) -> tuple[int, int]:
    """(total_purchase_count, total_points_issued) across all of this supplier's stores."""
    result = await session.execute(
        select(func.count(PointsTransaction.id), func.coalesce(func.sum(PointsTransaction.points), 0))
        .select_from(PointsTransaction)
        .join(Store, Store.id == PointsTransaction.store_id)
        .where(Store.supplier_id == supplier_id)
    )
    total_purchases, total_points = result.one()
    return int(total_purchases or 0), int(total_points or 0)


async def get_factory_overview(
    session: AsyncSession,
    date_from: date | None = None,
    date_to: date | None = None,
    kind: SupplierKind | None = None,
) -> FactoryOverview:
    """Dashboard data for the admin web app: KPI totals, a daily time series, a
    supplier-vs-wholesaler breakdown, and a top-10 ranking by points issued — all
    real aggregates over points_transactions, filtered by date range and/or kind."""
    if date_to is None:
        date_to = date.today()
    if date_from is None:
        date_from = date_to - timedelta(days=29)

    supplier_query = select(Supplier)
    if kind is not None:
        supplier_query = supplier_query.where(Supplier.kind == kind)
    suppliers_result = await session.execute(supplier_query)
    suppliers = list(suppliers_result.scalars().all())
    supplier_by_id = {s.id: s for s in suppliers}

    stores: list[Store] = []
    if supplier_by_id:
        stores_result = await session.execute(select(Store).where(Store.supplier_id.in_(supplier_by_id.keys())))
        stores = list(stores_result.scalars().all())
    supplier_id_by_store_id = {s.id: s.supplier_id for s in stores}

    counts_by_kind = {SupplierKind.SUPPLIER: 0, SupplierKind.WHOLESALER: 0}
    for s in suppliers:
        counts_by_kind[s.kind] = counts_by_kind.get(s.kind, 0) + 1

    store_ids = list(supplier_id_by_store_id.keys())
    range_filter = [
        PointsTransaction.store_id.in_(store_ids),
        func.date(PointsTransaction.created_at) >= date_from,
        func.date(PointsTransaction.created_at) <= date_to,
    ]

    total_purchases, total_points = 0, 0
    series_by_date: dict[str, tuple[int, int]] = {}
    per_supplier: dict[int, list[int]] = {s.id: [0, 0] for s in suppliers}

    if store_ids:
        totals_result = await session.execute(
            select(func.count(PointsTransaction.id), func.coalesce(func.sum(PointsTransaction.points), 0)).where(
                *range_filter
            )
        )
        total_purchases, total_points = totals_result.one()
        total_purchases, total_points = int(total_purchases or 0), int(total_points or 0)

        series_result = await session.execute(
            select(
                func.date(PointsTransaction.created_at),
                func.count(PointsTransaction.id),
                func.coalesce(func.sum(PointsTransaction.points), 0),
            )
            .where(*range_filter)
            .group_by(func.date(PointsTransaction.created_at))
        )
        series_by_date = {row[0].isoformat(): (int(row[1]), int(row[2])) for row in series_result.all()}

        per_store_result = await session.execute(
            select(
                PointsTransaction.store_id,
                func.count(PointsTransaction.id),
                func.coalesce(func.sum(PointsTransaction.points), 0),
            )
            .where(*range_filter)
            .group_by(PointsTransaction.store_id)
        )
        for store_id, count, points in per_store_result.all():
            supplier_id = supplier_id_by_store_id.get(store_id)
            if supplier_id in per_supplier:
                per_supplier[supplier_id][0] += int(count)
                per_supplier[supplier_id][1] += int(points)

    series = []
    cursor = date_from
    while cursor <= date_to:
        purchases, points = series_by_date.get(cursor.isoformat(), (0, 0))
        series.append(OverviewSeriesPoint(date=cursor.isoformat(), purchases=purchases, points_issued=points))
        cursor += timedelta(days=1)

    store_count_by_supplier: dict[int, int] = {}
    for store in stores:
        store_count_by_supplier[store.supplier_id] = store_count_by_supplier.get(store.supplier_id, 0) + 1

    by_kind_totals = {SupplierKind.SUPPLIER: [0, 0], SupplierKind.WHOLESALER: [0, 0]}
    for supplier_id, (count, points) in per_supplier.items():
        supplier_kind = supplier_by_id[supplier_id].kind
        by_kind_totals[supplier_kind][0] += count
        by_kind_totals[supplier_kind][1] += points

    by_kind = [
        OverviewKindBreakdown(kind=k.value, purchases=v[0], points_issued=v[1], entity_count=counts_by_kind.get(k, 0))
        for k, v in by_kind_totals.items()
    ]

    top = sorted(
        (
            OverviewTopEntity(
                id=supplier_id,
                name=supplier_by_id[supplier_id].name,
                kind=supplier_by_id[supplier_id].kind.value,
                store_count=store_count_by_supplier.get(supplier_id, 0),
                total_purchases=count,
                total_points_issued=points,
            )
            for supplier_id, (count, points) in per_supplier.items()
        ),
        key=lambda item: item.total_points_issued,
        reverse=True,
    )[:10]

    return FactoryOverview(
        totals=OverviewTotals(
            supplier_count=counts_by_kind.get(SupplierKind.SUPPLIER, 0),
            wholesaler_count=counts_by_kind.get(SupplierKind.WHOLESALER, 0),
            store_count=len(stores),
            total_purchases=total_purchases,
            total_points_issued=total_points,
        ),
        series=series,
        by_kind=by_kind,
        top=top,
    )


async def get_store_leaderboard(session: AsyncSession) -> list[StoreLeaderboardItem]:
    """All stores ranked by points issued, descending — feeds both the "Магазины" tab
    (full list) and the Главная top/bottom highlight (first/last N of this same list)."""
    stores_result = await session.execute(select(Store))
    stores = list(stores_result.scalars().all())
    stats = await _store_stats_map(session, [s.id for s in stores])

    supplier_ids = {s.supplier_id for s in stores}
    suppliers_by_id: dict[int, Supplier] = {}
    if supplier_ids:
        suppliers_result = await session.execute(select(Supplier).where(Supplier.id.in_(supplier_ids)))
        suppliers_by_id = {s.id: s for s in suppliers_result.scalars().all()}

    items = []
    for store in stores:
        count, points, _last_sale_at = stats.get(store.id, (0, 0, None))
        supplier = suppliers_by_id.get(store.supplier_id)
        items.append(
            StoreLeaderboardItem(
                store_id=store.id,
                store_name=store.name,
                city=store.city,
                supplier_name=supplier.name if supplier else None,
                sales_count=count,
                points_issued=points,
            )
        )
    items.sort(key=lambda i: i.points_issued, reverse=True)
    return items


async def get_seller_leaderboard(session: AsyncSession) -> list[SellerLeaderboardItem]:
    """All sellers ranked by points issued, descending — same shape/use as
    get_store_leaderboard above, one row per seller instead of per store."""
    result = await session.execute(
        select(
            PointsTransaction.seller_telegram_id,
            func.count(PointsTransaction.id),
            func.coalesce(func.sum(PointsTransaction.points), 0),
        )
        .where(PointsTransaction.seller_telegram_id.isnot(None))
        .group_by(PointsTransaction.seller_telegram_id)
    )
    stats = {row[0]: (int(row[1]), int(row[2])) for row in result.all()}

    sellers = await directory_service.list_sellers(session)
    items = []
    for seller in sellers:
        count, points = stats.get(seller.telegram_id, (0, 0))
        name = " ".join(part for part in [seller.first_name, seller.last_name] if part) or None
        items.append(
            SellerLeaderboardItem(
                telegram_id=seller.telegram_id,
                name=name,
                store_name=seller.store_name,
                supplier_name=seller.supplier_name,
                sales_count=count,
                points_issued=points,
            )
        )
    items.sort(key=lambda i: i.points_issued, reverse=True)
    return items


def _bottom_slice(ranked: list, highlight_count: int) -> list:
    """Last `highlight_count` items, excluding whatever the top slice already covers —
    plain [-n:] would overlap with [:n] once the list is between n+1 and 2n items long."""
    if len(ranked) <= highlight_count:
        return []
    return list(reversed(ranked[max(highlight_count, len(ranked) - highlight_count):]))


async def get_web_home(session: AsyncSession, highlight_count: int = 5) -> WebHomeOut:
    store_count_result = await session.execute(select(func.count(Store.id)))
    store_count = int(store_count_result.scalar_one() or 0)

    totals_result = await session.execute(
        select(
            func.count(PointsTransaction.id),
            func.coalesce(func.sum(PointsTransaction.amount), 0),
            func.coalesce(func.sum(PointsTransaction.points), 0),
        )
    )
    total_sales, total_amount, total_points = totals_result.one()

    stores = await get_store_leaderboard(session)
    sellers = await get_seller_leaderboard(session)

    return WebHomeOut(
        totals=WebHomeTotals(
            store_count=store_count,
            total_sales=int(total_sales or 0),
            total_amount=float(total_amount or 0),
            total_points_issued=int(total_points or 0),
        ),
        top_stores=stores[:highlight_count],
        bottom_stores=_bottom_slice(stores, highlight_count),
        top_sellers=sellers[:highlight_count],
        bottom_sellers=_bottom_slice(sellers, highlight_count),
    )
