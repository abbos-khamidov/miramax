"""Seed the loyalty-tier prize catalog and retire the old plumbing-parts catalog.

Safe to re-run: prizes are matched by name and updated. Anything active that isn't
in PRIZES is deactivated (not deleted — old rows may still be referenced by past
Redemption rows via product_id).
"""
import asyncio

from sqlalchemy import select

from core.db import async_session
from core.models import Product

CATEGORY = "Sovg'alar"

# (points_cost, name, image_url) — local static photos served by nginx from
# /var/www/miramax/bot/miniapp/dist/prizes after the miniapp build.
PRIZES = [
    (5, "Maxsus forma, Miramaxdan", "/bonuses/prizes/uniform.jpg?v=20260827c"),
    (10, "Dazmol", "/bonuses/prizes/iron.jpg?v=20260827c"),
    (15, "Premium dazmol", "/bonuses/prizes/premium-iron.jpg?v=20260827c"),
    (20, "Mikrotolqinli pech", "/bonuses/prizes/microwave.jpg?v=20260827c"),
    (25, "Changyutgich", "/bonuses/prizes/vacuum.jpg?v=20260827c"),
    (30, "32\" televizor", "/bonuses/prizes/tv.jpg?v=20260827c"),
    (40, "42\" televizor", "/bonuses/prizes/tv.jpg?v=20260827c"),
    (50, "55\" televizor", "/bonuses/prizes/tv.jpg?v=20260827c"),
    (100, "Kir yuvish mashinasi", "/bonuses/prizes/washing-machine.jpg?v=20260827c"),
    (150, "Muzlatkich", "/bonuses/prizes/fridge.jpg?v=20260827c"),
    (200, "1 kishilik umra", "/bonuses/prizes/umrah.jpg?v=20260827c"),
    (250, "iPhone 17", "/bonuses/prizes/iphone.jpg?v=20260827c"),
    (300, "2 kishilik umra", "/bonuses/prizes/umrah.jpg?v=20260827c"),
    (500, "30 000 000 so'm pul mukofoti", "/bonuses/prizes/money.jpg?v=20260827c"),
    (1000, "65 000 000 so'm pul mukofoti", "/bonuses/prizes/money.jpg?v=20260827c"),
    (1500, "100 000 000 so'm pul mukofoti", "/bonuses/prizes/money.jpg?v=20260827c"),
    (2000, "Labo", "/bonuses/prizes/labo.jpg?v=20260827c"),
    (3000, "Cobalt", "/bonuses/prizes/cobalt.jpg?v=20260827c"),
    (4000, "Tracker", "/bonuses/prizes/tracker.jpg?v=20260827c"),
    (5000, "BYD", "/bonuses/prizes/byd.jpg?v=20260827c"),
]


async def main() -> None:
    async with async_session() as session:
        keep_names = {name for _, name, _ in PRIZES}

        created = 0
        updated = 0
        for points_cost, name, icon in PRIZES:
            result = await session.execute(select(Product).where(Product.name == name))
            product = result.scalar_one_or_none()
            if product is None:
                session.add(
                    Product(name=name, category=CATEGORY, icon_or_image_url=icon, points_cost=points_cost, active=True)
                )
                created += 1
            else:
                product.category = CATEGORY
                product.icon_or_image_url = icon
                product.points_cost = points_cost
                product.active = True
                updated += 1

        retired_result = await session.execute(
            select(Product).where(Product.active.is_(True), Product.name.notin_(keep_names))
        )
        retired = 0
        for product in retired_result.scalars().all():
            product.active = False
            retired += 1

        await session.commit()
        print(f"Prizes seeded: created={created}, updated={updated}, old catalog retired={retired}")


if __name__ == "__main__":
    asyncio.run(main())
