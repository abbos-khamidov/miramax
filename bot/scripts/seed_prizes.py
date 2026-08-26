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

# (points_cost, name, icon) — from the client-provided prize list, cheapest first.
PRIZES = [
    (5, "Maxsus forma, Miramaxdan", "🎽"),
    (10, "Dazmol", "🧺"),
    (15, "Premium dazmol", "🧺"),
    (20, "Mikrotolqinli pech", "📡"),
    (25, "Changyutgich", "🧹"),
    (30, "32\" televizor", "📺"),
    (40, "42\" televizor", "📺"),
    (50, "55\" televizor", "📺"),
    (100, "Kir yuvish mashinasi", "🌀"),
    (150, "Muzlatkich", "❄️"),
    (200, "1 kishilik umra", "🕋"),
    (250, "iPhone 17", "📱"),
    (300, "2 kishilik umra", "🕋"),
    (500, "30 000 000 so'm pul mukofoti", "💰"),
    (1000, "65 000 000 so'm pul mukofoti", "💰"),
    (1500, "100 000 000 so'm pul mukofoti", "💰"),
    (2000, "Labo", "🚗"),
    (3000, "Cobalt", "🚗"),
    (4000, "Tracker", "🚗"),
    (5000, "BYD", "🚗"),
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
