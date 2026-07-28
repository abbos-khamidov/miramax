from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Store


async def create_store(session: AsyncSession, supplier_id: int, name: str, address: str | None, city: str | None) -> Store:
    store = Store(supplier_id=supplier_id, name=name, address=address, city=city)
    session.add(store)
    await session.commit()
    await session.refresh(store)
    return store


async def update_store(
    session: AsyncSession, store_id: int, name: str | None, address: str | None, city: str | None
) -> Store | None:
    store = await session.get(Store, store_id)
    if store is None:
        return None
    if name is not None:
        store.name = name
    if address is not None:
        store.address = address
    if city is not None:
        store.city = city
    await session.commit()
    await session.refresh(store)
    return store


async def list_stores_by_supplier(session: AsyncSession, supplier_id: int) -> list[Store]:
    result = await session.execute(select(Store).where(Store.supplier_id == supplier_id).order_by(Store.created_at))
    return list(result.scalars().all())


async def get_store(session: AsyncSession, store_id: int) -> Store | None:
    return await session.get(Store, store_id)
