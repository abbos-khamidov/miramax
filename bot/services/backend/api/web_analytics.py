from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Product
from core.schemas import (
    CityBreakdownItem,
    FactoryOverview,
    ProductOut,
    StoreLeaderboardItem,
    WebAdminItem,
    WebHomeOut,
    WebUserItem,
    WebUsersPage,
)
from core.services import directory as directory_service
from core.services import web_auth
from core.services.analytics import get_city_breakdown, get_factory_overview, get_store_leaderboard, get_web_home
from services.backend.deps import get_db

router = APIRouter(prefix="/api/web", tags=["web-analytics"])


class LoginIn(BaseModel):
    login: str
    password: str


class LoginOut(BaseModel):
    token: str


@router.post("/login", response_model=LoginOut)
async def login(payload: LoginIn) -> LoginOut:
    if not web_auth.verify_credentials(payload.login, payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    return LoginOut(token=web_auth.issue_token())


async def require_web_session(authorization: str = Header(..., alias="Authorization")) -> None:
    token = authorization.removeprefix("Bearer ").strip()
    if not web_auth.verify_token(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired session")


@router.get("/analytics", response_model=FactoryOverview)
async def web_analytics(
    session: AsyncSession = Depends(get_db),
    _auth: None = Depends(require_web_session),
) -> FactoryOverview:
    return await get_factory_overview(session)


@router.get("/home", response_model=WebHomeOut)
async def web_home(
    session: AsyncSession = Depends(get_db),
    _auth: None = Depends(require_web_session),
) -> WebHomeOut:
    return await get_web_home(session)


@router.get("/stores", response_model=list[StoreLeaderboardItem])
async def web_stores(
    session: AsyncSession = Depends(get_db),
    _auth: None = Depends(require_web_session),
) -> list[StoreLeaderboardItem]:
    return await get_store_leaderboard(session)


@router.get("/products", response_model=list[ProductOut])
async def web_products(
    session: AsyncSession = Depends(get_db),
    _auth: None = Depends(require_web_session),
) -> list[ProductOut]:
    result = await session.execute(select(Product).order_by(Product.created_at.desc(), Product.id.desc()))
    return list(result.scalars().all())


@router.get("/cities", response_model=list[CityBreakdownItem])
async def web_cities(
    session: AsyncSession = Depends(get_db),
    _auth: None = Depends(require_web_session),
) -> list[CityBreakdownItem]:
    return await get_city_breakdown(session)


@router.get("/admins", response_model=list[WebAdminItem])
async def web_admins(
    session: AsyncSession = Depends(get_db),
    _auth: None = Depends(require_web_session),
) -> list[WebAdminItem]:
    admins = await directory_service.list_admins(session)
    return [
        WebAdminItem(telegram_id=a.telegram_id, first_name=a.first_name, last_name=a.last_name, phone=a.phone)
        for a in admins
    ]


_USER_CATEGORIES = {"admin", "supplier", "wholesaler", "client"}


@router.get("/users", response_model=WebUsersPage)
async def web_users(
    category: str,
    page: int = 1,
    page_size: int = 10,
    session: AsyncSession = Depends(get_db),
    _auth: None = Depends(require_web_session),
) -> WebUsersPage:
    if category not in _USER_CATEGORIES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="unknown category")
    page = max(page, 1)
    page_size = max(1, min(page_size, 50))

    rows = await directory_service.list_web_users(session, category)
    start = (page - 1) * page_size
    page_rows = rows[start : start + page_size]
    return WebUsersPage(
        items=[WebUserItem(id=r.id, name=r.name, phone=r.phone) for r in page_rows],
        total=len(rows),
        page=page,
        page_size=page_size,
    )
