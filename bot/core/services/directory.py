from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import InviteCode, InviteTargetRole, Role, RoleName, Supplier, SupplierKind


def _digits(value: str | None) -> str:
    """Strips everything but digits so phone search ignores +, spaces and dashes
    regardless of how the number was typed at creation time vs. search time."""
    return "".join(ch for ch in (value or "") if ch.isdigit())


async def list_suppliers(session: AsyncSession, kind: SupplierKind) -> list[Supplier]:
    result = await session.execute(select(Supplier).where(Supplier.kind == kind).order_by(Supplier.created_at.desc()))
    return list(result.scalars().all())


async def search_suppliers_by_phone(session: AsyncSession, kind: SupplierKind, phone_query: str) -> list[Supplier]:
    query_digits = _digits(phone_query)
    if not query_digits:
        return []
    suppliers = await list_suppliers(session, kind)
    return [s for s in suppliers if query_digits in _digits(s.contact_phone)]


async def get_supplier(session: AsyncSession, supplier_id: int) -> Supplier | None:
    return await session.get(Supplier, supplier_id)


class AdminEntry:
    """Admins/Factory have no name field on `Role` — their contact info (if any) is
    recovered from the admin invite they redeemed. The original seeded Factory
    account was never invited, so it has none."""

    def __init__(self, telegram_id: int, first_name: str | None, last_name: str | None, phone: str | None):
        self.telegram_id = telegram_id
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone


async def list_admins(session: AsyncSession) -> list[AdminEntry]:
    roles_result = await session.execute(select(Role).where(Role.role.in_([RoleName.FACTORY, RoleName.ADMIN])))
    roles = list(roles_result.scalars().all())

    invites_result = await session.execute(
        select(InviteCode).where(
            InviteCode.target_role == InviteTargetRole.ADMIN, InviteCode.used_by_telegram_id.isnot(None)
        )
    )
    invite_by_telegram_id = {inv.used_by_telegram_id: inv for inv in invites_result.scalars().all()}

    entries = []
    for role in roles:
        invite = invite_by_telegram_id.get(role.telegram_id)
        entries.append(
            AdminEntry(
                telegram_id=role.telegram_id,
                first_name=invite.contact_first_name if invite else None,
                last_name=invite.contact_last_name if invite else None,
                phone=invite.contact_phone if invite else None,
            )
        )
    return entries


async def search_admins_by_phone(session: AsyncSession, phone_query: str) -> list[AdminEntry]:
    query_digits = _digits(phone_query)
    if not query_digits:
        return []
    admins = await list_admins(session)
    return [a for a in admins if a.phone and query_digits in _digits(a.phone)]
