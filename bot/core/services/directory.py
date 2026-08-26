from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import CustomerCard, InviteCode, InviteTargetRole, Role, RoleName, Store, Supplier, SupplierKind


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


class SellerEntry:
    """Sellers have no name field on `Role` either — same recovery-from-invite pattern
    as AdminEntry, plus the store/supplier they're bound to for display."""

    def __init__(
        self,
        telegram_id: int,
        first_name: str | None,
        last_name: str | None,
        store_id: int | None,
        store_name: str | None,
        supplier_name: str | None,
    ):
        self.telegram_id = telegram_id
        self.first_name = first_name
        self.last_name = last_name
        self.store_id = store_id
        self.store_name = store_name
        self.supplier_name = supplier_name


async def list_sellers(session: AsyncSession) -> list[SellerEntry]:
    roles_result = await session.execute(select(Role).where(Role.role == RoleName.SELLER))
    roles = list(roles_result.scalars().all())

    invites_result = await session.execute(
        select(InviteCode).where(
            InviteCode.target_role == InviteTargetRole.SELLER, InviteCode.used_by_telegram_id.isnot(None)
        )
    )
    invite_by_telegram_id = {inv.used_by_telegram_id: inv for inv in invites_result.scalars().all()}

    store_ids = {r.store_id for r in roles if r.store_id is not None}
    stores_by_id: dict[int, Store] = {}
    if store_ids:
        stores_result = await session.execute(select(Store).where(Store.id.in_(store_ids)))
        stores_by_id = {s.id: s for s in stores_result.scalars().all()}

    supplier_ids = {s.supplier_id for s in stores_by_id.values()}
    suppliers_by_id: dict[int, Supplier] = {}
    if supplier_ids:
        suppliers_result = await session.execute(select(Supplier).where(Supplier.id.in_(supplier_ids)))
        suppliers_by_id = {s.id: s for s in suppliers_result.scalars().all()}

    entries = []
    for role in roles:
        invite = invite_by_telegram_id.get(role.telegram_id)
        store = stores_by_id.get(role.store_id) if role.store_id is not None else None
        supplier = suppliers_by_id.get(store.supplier_id) if store is not None else None
        entries.append(
            SellerEntry(
                telegram_id=role.telegram_id,
                first_name=invite.contact_first_name if invite else None,
                last_name=invite.contact_last_name if invite else None,
                store_id=store.id if store else None,
                store_name=store.name if store else None,
                supplier_name=supplier.name if supplier else None,
            )
        )
    return entries


class WebUserRow:
    def __init__(self, id: int | None, name: str, phone: str | None):
        self.id = id
        self.name = name
        self.phone = phone


async def list_web_users(session: AsyncSession, category: str) -> list[WebUserRow]:
    """One flat name+phone list per category, for the admin analytics site's
    Users page — admins/suppliers/wholesalers have no name on Role/Supplier
    directly for admins (recovered from their invite), suppliers/wholesalers use
    their own contact fields, clients use CustomerCard directly."""
    if category == "admin":
        admins = await list_admins(session)
        return [
            WebUserRow(
                id=a.telegram_id,
                name=" ".join(part for part in [a.first_name, a.last_name] if part) or "—",
                phone=a.phone,
            )
            for a in admins
        ]
    if category in ("supplier", "wholesaler"):
        kind = SupplierKind.SUPPLIER if category == "supplier" else SupplierKind.WHOLESALER
        suppliers = await list_suppliers(session, kind)
        return [
            WebUserRow(
                id=s.id,
                name=" ".join(part for part in [s.contact_first_name, s.contact_last_name] if part) or s.name,
                phone=s.contact_phone,
            )
            for s in suppliers
        ]
    if category == "client":
        result = await session.execute(select(CustomerCard).order_by(CustomerCard.created_at.desc()))
        customers = list(result.scalars().all())
        return [WebUserRow(id=c.id, name=c.full_name or "—", phone=c.phone) for c in customers]
    return []
