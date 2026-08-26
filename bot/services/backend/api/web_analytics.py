from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.schemas import FactoryOverview
from core.services import web_auth
from core.services.analytics import get_factory_overview
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
