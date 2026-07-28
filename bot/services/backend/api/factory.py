from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import SupplierKind
from core.schemas import (
    AdminCreateIn,
    AdminInviteOut,
    AdminListItem,
    SupplierCreateIn,
    SupplierDetail,
    SupplierInviteOut,
    SupplierListItem,
)
from core.services import directory as directory_service
from core.services import invites as invites_service
from core.services import stores as stores_service
from core.services.analytics import get_supplier_analytics, get_supplier_purchase_stats
from services.backend.deps import Principal, get_db, require_factory

router = APIRouter(prefix="/api/factory", tags=["factory"])


def _parse_kind(kind: str | None) -> SupplierKind | None:
    if kind is None:
        return None
    try:
        return SupplierKind(kind)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid kind") from None


@router.post("/suppliers", response_model=SupplierInviteOut)
async def create_supplier(
    payload: SupplierCreateIn,
    session: AsyncSession = Depends(get_db),
    _principal: Principal = Depends(require_factory),
) -> SupplierInviteOut:
    kind = _parse_kind(payload.kind) or SupplierKind.SUPPLIER
    invite, link = await invites_service.create_supplier_invite(
        session,
        company_name=payload.company_name,
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone=payload.phone,
        city=payload.city,
        kind=kind,
    )
    return SupplierInviteOut(
        supplier_id=invite.supplier_id,
        supplier_name=payload.company_name,
        kind=kind.value,
        code=invite.code,
        link=link,
    )


@router.post("/admins", response_model=AdminInviteOut)
async def create_admin(
    payload: AdminCreateIn,
    session: AsyncSession = Depends(get_db),
    _principal: Principal = Depends(require_factory),
) -> AdminInviteOut:
    invite, link = await invites_service.create_admin_invite(
        session, first_name=payload.first_name, last_name=payload.last_name, phone=payload.phone
    )
    return AdminInviteOut(code=invite.code, link=link)


@router.get("/suppliers", response_model=list[SupplierListItem])
async def list_suppliers(
    kind: str | None = None,
    search: str | None = None,
    session: AsyncSession = Depends(get_db),
    _principal: Principal = Depends(require_factory),
) -> list[SupplierListItem]:
    parsed_kind = _parse_kind(kind)

    if search:
        results: list = []
        for candidate_kind in [parsed_kind] if parsed_kind else [SupplierKind.SUPPLIER, SupplierKind.WHOLESALER]:
            results.extend(await directory_service.search_suppliers_by_phone(session, candidate_kind, search))
        suppliers = results
        if not suppliers:
            pattern = search.strip().lower()
            all_suppliers = []
            for candidate_kind in [parsed_kind] if parsed_kind else [SupplierKind.SUPPLIER, SupplierKind.WHOLESALER]:
                all_suppliers.extend(await directory_service.list_suppliers(session, candidate_kind))
            suppliers = [s for s in all_suppliers if pattern in s.name.lower()]
    elif parsed_kind is not None:
        suppliers = await directory_service.list_suppliers(session, parsed_kind)
    else:
        suppliers = await directory_service.list_suppliers(
            session, SupplierKind.SUPPLIER
        ) + await directory_service.list_suppliers(session, SupplierKind.WHOLESALER)

    items = []
    for supplier in suppliers:
        stores = await stores_service.list_stores_by_supplier(session, supplier.id)
        total_purchases, total_points = await get_supplier_purchase_stats(session, supplier.id)
        items.append(
            SupplierListItem(
                id=supplier.id,
                name=supplier.name,
                kind=supplier.kind.value,
                city=supplier.city,
                contact_first_name=supplier.contact_first_name,
                contact_last_name=supplier.contact_last_name,
                contact_phone=supplier.contact_phone,
                store_count=len(stores),
                total_purchases=total_purchases,
                total_points_issued=total_points,
                created_at=supplier.created_at,
            )
        )
    items.sort(key=lambda i: i.created_at, reverse=True)
    return items


@router.get("/admins", response_model=list[AdminListItem])
async def list_admins(
    session: AsyncSession = Depends(get_db),
    _principal: Principal = Depends(require_factory),
) -> list[AdminListItem]:
    admins = await directory_service.list_admins(session)
    return [
        AdminListItem(telegram_id=a.telegram_id, first_name=a.first_name, last_name=a.last_name, phone=a.phone)
        for a in admins
    ]


@router.get("/suppliers/{supplier_id}", response_model=SupplierDetail)
async def get_supplier_detail(
    supplier_id: int,
    session: AsyncSession = Depends(get_db),
    _principal: Principal = Depends(require_factory),
) -> SupplierDetail:
    supplier = await directory_service.get_supplier(session, supplier_id)
    if supplier is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="supplier not found")

    analytics = await get_supplier_analytics(session, supplier_id)
    total_purchases, total_points = await get_supplier_purchase_stats(session, supplier_id)

    return SupplierDetail(
        id=supplier.id,
        name=supplier.name,
        kind=supplier.kind.value,
        city=supplier.city,
        contact_first_name=supplier.contact_first_name,
        contact_last_name=supplier.contact_last_name,
        contact_phone=supplier.contact_phone,
        created_at=supplier.created_at,
        total_purchases=total_purchases,
        total_points_issued=total_points,
        stores=analytics.stores if analytics else [],
    )
