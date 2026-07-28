"""Seed client-facing catalog products for local testing.

Safe to re-run: products are matched by name and updated.
"""
import asyncio

from sqlalchemy import select

from core.db import async_session
from core.models import Product

PRODUCTS = [
    ("Miramax Classic смеситель", "Смесители", "https://placehold.co/900x650/0f766e/ffffff?text=Miramax+Classic", 1200),
    ("Miramax Lux смеситель", "Смесители", "https://placehold.co/900x650/2563eb/ffffff?text=Miramax+Lux", 1800),
    ("Душевой комплект Basic", "Душ", "https://placehold.co/900x650/0891b2/ffffff?text=Dush+Basic", 950),
    ("Душевой комплект Premium", "Душ", "https://placehold.co/900x650/7c3aed/ffffff?text=Dush+Premium", 2100),
    ("Кухонный кран Mono", "Кухня", "https://placehold.co/900x650/16a34a/ffffff?text=Kran+Mono", 1350),
    ("Кухонный кран Flex", "Кухня", "https://placehold.co/900x650/ea580c/ffffff?text=Kran+Flex", 2400),
    ("Сифон стандарт", "Аксессуары", "https://placehold.co/900x650/475569/ffffff?text=Sifon", 450),
    ("Шланг душевой", "Аксессуары", "https://placehold.co/900x650/64748b/ffffff?text=Shlang", 300),
    ("Лейка душевая", "Аксессуары", "https://placehold.co/900x650/0d9488/ffffff?text=Leyka", 550),
    ("Набор монтажный", "Аксессуары", "https://placehold.co/900x650/be123c/ffffff?text=Montaj", 700),
    ("Miramax Comfort смеситель", "Смесители", "https://placehold.co/900x650/0f766e/ffffff?text=Comfort", 1400),
    ("Miramax Grand смеситель", "Смесители", "https://placehold.co/900x650/2563eb/ffffff?text=Grand", 2200),
    ("Смеситель для ванны Wave", "Смесители", "https://placehold.co/900x650/1d4ed8/ffffff?text=Wave", 1650),
    ("Термостатический смеситель", "Смесители", "https://placehold.co/900x650/1e40af/ffffff?text=Termo", 2600),
    ("Душевой комплект Compact", "Душ", "https://placehold.co/900x650/0891b2/ffffff?text=Compact", 800),
    ("Тропический душ Rain", "Душ", "https://placehold.co/900x650/7c3aed/ffffff?text=Rain", 3200),
    ("Ручной душ хром", "Душ", "https://placehold.co/900x650/6d28d9/ffffff?text=Ruchnoy", 620),
    ("Штанга душевая", "Душ", "https://placehold.co/900x650/5b21b6/ffffff?text=Shtanga", 480),
    ("Кухонный кран Wide", "Кухня", "https://placehold.co/900x650/16a34a/ffffff?text=Wide", 1750),
    ("Кухонный кран Compact", "Кухня", "https://placehold.co/900x650/15803d/ffffff?text=Kompakt", 1100),
    ("Фильтр для крана", "Кухня", "https://placehold.co/900x650/166534/ffffff?text=Filtr", 350),
    ("Дозатор для мыла", "Кухня", "https://placehold.co/900x650/065f46/ffffff?text=Dozator", 280),
    ("Прокладки набор", "Аксессуары", "https://placehold.co/900x650/64748b/ffffff?text=Prokladki", 150),
    ("Аэратор для крана", "Аксессуары", "https://placehold.co/900x650/475569/ffffff?text=Aerator", 200),
    ("Держатель для душа", "Аксессуары", "https://placehold.co/900x650/334155/ffffff?text=Derjatel", 320),
    ("Гибкая подводка", "Аксессуары", "https://placehold.co/900x650/1f2937/ffffff?text=Podvodka", 260),
    ("Смеситель для биде", "Смесители", "https://placehold.co/900x650/0f766e/ffffff?text=Bide", 1300),
    ("Смеситель настенный", "Смесители", "https://placehold.co/900x650/2563eb/ffffff?text=Nastenniy", 1900),
    ("Душевой уголок стекло", "Душ", "https://placehold.co/900x650/0891b2/ffffff?text=Ugolok", 4500),
    ("Поддон душевой", "Душ", "https://placehold.co/900x650/7c3aed/ffffff?text=Poddon", 3800),
]


async def main() -> None:
    async with async_session() as session:
        created = 0
        updated = 0
        for name, category, image_url, points_cost in PRODUCTS:
            result = await session.execute(select(Product).where(Product.name == name))
            product = result.scalar_one_or_none()
            if product is None:
                session.add(
                    Product(
                        name=name,
                        category=category,
                        icon_or_image_url=image_url,
                        points_cost=points_cost,
                        active=True,
                    )
                )
                created += 1
            else:
                product.category = category
                product.icon_or_image_url = image_url
                product.points_cost = points_cost
                product.active = True
                updated += 1
        await session.commit()
        print(f"Seeded client products: created={created}, updated={updated}")


if __name__ == "__main__":
    asyncio.run(main())
