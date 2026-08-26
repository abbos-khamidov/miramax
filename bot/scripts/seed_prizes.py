"""Seed the loyalty-tier prize catalog and retire the old plumbing-parts catalog.

Safe to re-run: prizes are matched by name and updated. Anything active that isn't
in PRIZES is deactivated (not deleted — old rows may still be referenced by past
Redemption rows via product_id).
"""
import asyncio
from urllib.parse import quote

from sqlalchemy import select

from core.db import async_session
from core.models import Product

CATEGORY = "Sovg'alar"

# (points_cost, name, icon_or_image_url) — from the client-provided prize list, cheapest
# first. Real photos are Wikimedia Commons Special:FilePath URLs (stable, hotlink-safe
# canonical redirects) — illustrative only, not Miramax's own product photography.
def _commons(filename: str) -> str:
    return "https://commons.wikimedia.org/wiki/Special:FilePath/" + quote(filename)

PRIZES = [
    # Generic workwear/coveralls photo (no logo) standing in for the branded uniform —
    # a real Miramax-branded photo should replace this once the client supplies one.
    (5, "Maxsus forma, Miramaxdan", _commons("Worker_with_cylinders_-_DPLA_-_bb6dd856b0c64965fb55fff4a2351bb2.jpg")),
    (10, "Dazmol", _commons("ClothesIron.JPG")),
    (15, "Premium dazmol", _commons("Electric_steam_iron.jpg")),
    (20, "Mikrotolqinli pech", _commons("Microwave_oven.jpg")),
    (25, "Changyutgich", _commons("Vacuum_cleaner.jpg")),
    (30, "32\" televizor", _commons("Television_LCD_50_Pulgadas.JPG")),
    (40, "42\" televizor", _commons("Television_LCD_50_Pulgadas.JPG")),
    (50, "55\" televizor", _commons("Television_LCD_50_Pulgadas.JPG")),
    (100, "Kir yuvish mashinasi", _commons("Washing_Machine_Beko.jpg")),
    (150, "Muzlatkich", _commons("Fridge.jpg")),
    (200, "1 kishilik umra", _commons("Kaaba_Mecca.jpg")),
    (250, "iPhone 17", _commons("White_iPhone_17.jpg")),
    (300, "2 kishilik umra", _commons("Kaaba_Mecca.jpg")),
    (500, "30 000 000 so'm pul mukofoti", _commons("50000_soms_of_Uzbekistan_(2017)_obverse.jpg")),
    (1000, "65 000 000 so'm pul mukofoti", _commons("50000_soms_of_Uzbekistan_(2017)_obverse.jpg")),
    (1500, "100 000 000 so'm pul mukofoti", _commons("50000_soms_of_Uzbekistan_(2017)_obverse.jpg")),
    (2000, "Labo", _commons("GM Labo. Muqimiy street, Tashkent, Uzbekistan 01.jpg")),
    (3000, "Cobalt", _commons("Chevrolet_Cobalt_1.8_LTZ_2017_(38346300391).jpg")),
    (4000, "Tracker", _commons("2022_Chevrolet_Tracker_1.2_Turbo_LS.jpg")),
    (5000, "BYD", _commons("BYD_Atto_3_front-left.jpg")),
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
