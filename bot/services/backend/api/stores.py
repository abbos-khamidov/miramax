from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from services.backend.deps import Principal, get_current_principal, get_db, require_own_supplier
from core.schemas import InviteOut, InviteSellerIn, StoreCreate, StoreOut, StoreUpdate
from core.services import invites as invites_service
from core.services import stores as stores_service

router = APIRouter(prefix="/api", tags=["stores"])


@router.get("/suppliers/{supplier_id}/stores", response_model=list[StoreOut])
async def list_supplier_stores(
    supplier_id: int,
    session: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
) -> list[StoreOut]:
    require_own_supplier(supplier_id, principal)
    return await stores_service.list_stores_by_supplier(session, supplier_id)


@router.post("/stores", response_model=StoreOut, status_code=status.HTTP_201_CREATED)
async def create_store(
    payload: StoreCreate,
    session: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
) -> StoreOut:
    require_own_supplier(payload.supplier_id, principal)
    return await stores_service.create_store(session, payload.supplier_id, payload.name, payload.address, payload.city)


@router.put("/stores/{store_id}", response_model=StoreOut)
async def update_store(
    store_id: int,
    payload: StoreUpdate,
    session: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
) -> StoreOut:
    store = await stores_service.get_store(session, store_id)
    if store is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="store not found")
    require_own_supplier(store.supplier_id, principal)

    updated = await stores_service.update_store(session, store_id, payload.name, payload.address, payload.city)
    return updated


@router.post("/stores/{store_id}/invite-seller", response_model=InviteOut)
async def invite_seller(
    store_id: int,
    payload: InviteSellerIn,
    session: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
) -> InviteOut:
    store = await stores_service.get_store(session, store_id)
    if store is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="store not found")
    require_own_supplier(store.supplier_id, principal)

    _invite, link = await invites_service.create_seller_invite(
        session, store_id, first_name=payload.first_name, last_name=payload.last_name
    )
    return InviteOut(code=_invite.code, link=link)
