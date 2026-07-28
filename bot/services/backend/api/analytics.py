from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from services.backend.deps import Principal, get_db, require_factory, require_own_supplier, get_current_principal
from core.models import SupplierKind
from core.schemas import FactoryAnalytics, FactoryOverview, SupplierAnalytics
from core.services import analytics as analytics_service
from fastapi import HTTPException, status

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/factory/overview", response_model=FactoryOverview)
async def factory_overview(
    date_from: date | None = None,
    date_to: date | None = None,
    kind: str | None = None,
    session: AsyncSession = Depends(get_db),
    _principal: Principal = Depends(require_factory),
) -> FactoryOverview:
    parsed_kind = None
    if kind:
        try:
            parsed_kind = SupplierKind(kind)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid kind") from None
    return await analytics_service.get_factory_overview(session, date_from=date_from, date_to=date_to, kind=parsed_kind)


@router.get("/analytics/factory", response_model=FactoryAnalytics)
async def factory_analytics(
    period: str | None = None,
    supplier_id: int | None = None,
    store_id: int | None = None,
    session: AsyncSession = Depends(get_db),
    _principal: Principal = Depends(require_factory),
) -> FactoryAnalytics:
    # `period` is accepted for API-contract parity with future phases; there is no
    # sales/transactions data yet (out of scope for phase 1), so it has no effect today.
    return await analytics_service.get_factory_analytics(session, supplier_id=supplier_id, store_id=store_id)


@router.get("/suppliers/{supplier_id}/analytics", response_model=SupplierAnalytics)
async def supplier_analytics(
    supplier_id: int,
    period: str | None = None,
    session: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
) -> SupplierAnalytics:
    require_own_supplier(supplier_id, principal)
    result = await analytics_service.get_supplier_analytics(session, supplier_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="supplier not found")
    return result
