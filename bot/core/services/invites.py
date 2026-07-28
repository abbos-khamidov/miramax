import secrets
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.models import CustomerCard, InviteCode, InviteTargetRole, Role, RoleName, Supplier, SupplierKind


def _new_code() -> str:
    return f"inv_{secrets.token_urlsafe(8)}"


_BOT_USERNAME_BY_TARGET_ROLE = {
    InviteTargetRole.CUSTOMER: lambda: settings.bot_username,
    InviteTargetRole.SUPPLIER: lambda: settings.seller_bot_username,
    InviteTargetRole.SELLER: lambda: settings.seller_bot_username,
    InviteTargetRole.ADMIN: lambda: settings.admin_bot_username,
}


def _link_for(code: str, target_role: InviteTargetRole) -> str:
    bot_username = _BOT_USERNAME_BY_TARGET_ROLE[target_role]()
    return f"https://t.me/{bot_username}?start={code}"


async def create_supplier_invite(
    session: AsyncSession,
    company_name: str,
    first_name: str,
    last_name: str,
    phone: str,
    city: str | None = None,
    kind: SupplierKind = SupplierKind.SUPPLIER,
) -> tuple[InviteCode, str]:
    """Factory onboards a brand-new supplier/wholesaler company + its first contact in one shot.

    Wholesaler is just a label on the Supplier row for Factory-side bookkeeping — once
    the invite is redeemed, a wholesaler behaves identically to a supplier in seller_bot.
    """
    supplier = Supplier(
        name=company_name,
        kind=kind,
        contact_first_name=first_name,
        contact_last_name=last_name,
        contact_phone=phone,
        city=city,
    )
    session.add(supplier)
    await session.flush()

    invite = InviteCode(
        code=_new_code(),
        target_role=InviteTargetRole.SUPPLIER,
        supplier_id=supplier.id,
        contact_first_name=first_name,
        contact_last_name=last_name,
        contact_phone=phone,
    )
    session.add(invite)
    await session.commit()
    await session.refresh(invite)
    return invite, _link_for(invite.code, InviteTargetRole.SUPPLIER)


async def create_seller_invite(
    session: AsyncSession, store_id: int, first_name: str, last_name: str
) -> tuple[InviteCode, str]:
    invite = InviteCode(
        code=_new_code(),
        target_role=InviteTargetRole.SELLER,
        store_id=store_id,
        contact_first_name=first_name,
        contact_last_name=last_name,
    )
    session.add(invite)
    await session.commit()
    await session.refresh(invite)
    return invite, _link_for(invite.code, InviteTargetRole.SELLER)


async def create_customer_invite(
    session: AsyncSession, customer_card_id: int, first_name: str, phone: str
) -> tuple[InviteCode, str]:
    """A seller pre-registers a customer who hasn't opened the customer bot yet — the
    QR links their eventual telegram_id back to the CustomerCard the seller just created."""
    invite = InviteCode(
        code=_new_code(),
        target_role=InviteTargetRole.CUSTOMER,
        customer_card_id=customer_card_id,
        contact_first_name=first_name,
        contact_phone=phone,
    )
    session.add(invite)
    await session.commit()
    await session.refresh(invite)
    return invite, _link_for(invite.code, InviteTargetRole.CUSTOMER)


async def create_admin_invite(
    session: AsyncSession, first_name: str, last_name: str, phone: str
) -> tuple[InviteCode, str]:
    """An existing Factory/Admin promotes someone else to Admin via QR — same pattern as
    supplier/wholesaler invites, redeemed inside admin_bot itself."""
    invite = InviteCode(
        code=_new_code(),
        target_role=InviteTargetRole.ADMIN,
        contact_first_name=first_name,
        contact_last_name=last_name,
        contact_phone=phone,
    )
    session.add(invite)
    await session.commit()
    await session.refresh(invite)
    return invite, _link_for(invite.code, InviteTargetRole.ADMIN)


class InviteAlreadyUsedError(Exception):
    pass


class InviteNotFoundError(Exception):
    pass


class AlreadyHasRoleError(Exception):
    """Raised when redeeming would silently overwrite a role someone was manually
    assigned (e.g. factory/admin) — invites must never be able to clobber that."""

    def __init__(self, existing_role: RoleName):
        self.existing_role = existing_role


async def redeem_invite(session: AsyncSession, code: str, telegram_id: int) -> InviteCode:
    result = await session.execute(select(InviteCode).where(InviteCode.code == code))
    invite = result.scalar_one_or_none()
    if invite is None:
        raise InviteNotFoundError(code)
    if invite.used_at is not None:
        raise InviteAlreadyUsedError(code)

    if invite.target_role != InviteTargetRole.CUSTOMER:
        existing_role_result = await session.execute(select(Role).where(Role.telegram_id == telegram_id))
        existing_role = existing_role_result.scalar_one_or_none()
        if existing_role is not None:
            raise AlreadyHasRoleError(existing_role.role)

    invite.used_by_telegram_id = telegram_id
    invite.used_at = datetime.now(timezone.utc)

    if invite.target_role == InviteTargetRole.CUSTOMER:
        customer = await session.get(CustomerCard, invite.customer_card_id)
        if customer is not None:
            customer.telegram_id = telegram_id
    else:
        if invite.target_role == InviteTargetRole.SUPPLIER:
            new_role, new_supplier_id, new_store_id = RoleName.SUPPLIER, invite.supplier_id, None
        elif invite.target_role == InviteTargetRole.SELLER:
            new_role, new_supplier_id, new_store_id = RoleName.SELLER, None, invite.store_id
        else:
            new_role, new_supplier_id, new_store_id = RoleName.ADMIN, None, None

        session.add(Role(telegram_id=telegram_id, role=new_role, supplier_id=new_supplier_id, store_id=new_store_id))

    await session.commit()
    await session.refresh(invite)
    return invite
