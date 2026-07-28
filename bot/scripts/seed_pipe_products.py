"""Seed the real Miramax pipe catalog from `miramax products/1/` and retire the
old placeholder bathroom-fixture products seeded by seed_client_products.py.

Photos are uploaded once via the client bot to SEED_FACTORY_TELEGRAM_ID (must have
already pressed /start on the client bot at least once) to obtain a Telegram file_id —
there's no public HTTPS host for local images yet, and Telegram needs one to fetch a
photo by URL, so file_id (bot-scoped, reusable forever) is the pragmatic stand-in.

Safe to re-run: products are matched by name and updated; photo upload is skipped for
products that already have an icon_or_image_url.
"""
import asyncio
from pathlib import Path

from aiogram import Bot
from aiogram.types import FSInputFile
from sqlalchemy import select

from core.config import settings
from core.db import async_session
from core.models import Product

PRODUCTS_DIR = Path(__file__).resolve().parent.parent / "miramax products" / "1"

# (filename, product name, category, points_cost placeholder — real pricing TBD)
PRODUCTS = [
    ("pert truba.png", "PERT труба", "Трубы", 400),
    ("pex truba.png", "PEX труба", "Трубы", 450),
    ("pn10 cold water.png", "Труба PN10 — холодная вода", "Трубы", 350),
    ("pn16 cold.png", "Труба PN16 — холодная вода", "Трубы", 450),
    ("pn20 cold.png", "Труба PN20 — холодная вода", "Трубы", 550),
    ("pn25 hot.png", "Труба PN25 — горячая вода", "Трубы", 650),
    ("xbc pn 10.png", "XBC труба PN10", "Трубы", 500),
    ("xbc pn 16.png", "XBC труба PN16", "Трубы", 600),
    ("гbc.png", "ГBC труба", "Трубы", 500),
]

OLD_PLACEHOLDER_NAMES = [
    "Miramax Classic смеситель", "Miramax Lux смеситель", "Душевой комплект Basic",
    "Душевой комплект Premium", "Кухонный кран Mono", "Кухонный кран Flex",
    "Сифон стандарт", "Шланг душевой", "Лейка душевая", "Набор монтажный",
    "Miramax Comfort смеситель", "Miramax Grand смеситель", "Смеситель для ванны Wave",
    "Термостатический смеситель", "Душевой комплект Compact", "Тропический душ Rain",
    "Ручной душ хром", "Штанга душевая", "Кухонный кран Wide", "Кухонный кран Compact",
    "Фильтр для крана", "Дозатор для мыла", "Прокладки набор", "Аэратор для крана",
    "Держатель для душа", "Гибкая подводка", "Смеситель для биде", "Смеситель настенный",
    "Душевой уголок стекло", "Поддон душевой",
]


async def main() -> None:
    async with async_session() as session:
        created = 0
        updated = 0
        for filename, name, category, points_cost in PRODUCTS:
            result = await session.execute(select(Product).where(Product.name == name))
            product = result.scalar_one_or_none()
            if product is None:
                product = Product(name=name, category=category, points_cost=points_cost, active=True)
                session.add(product)
                created += 1
            else:
                product.category = category
                product.points_cost = points_cost
                product.active = True
                updated += 1
        await session.commit()
        print(f"Real pipe products: created={created}, updated={updated}")

        retired = 0
        result = await session.execute(select(Product).where(Product.name.in_(OLD_PLACEHOLDER_NAMES)))
        for product in result.scalars().all():
            if product.active:
                product.active = False
                retired += 1
        await session.commit()
        print(f"Retired old placeholder products: {retired}")

        bot = Bot(token=settings.bot_token)
        uploaded, skipped, failed = 0, 0, 0
        try:
            for filename, name, _category, _points in PRODUCTS:
                result = await session.execute(select(Product).where(Product.name == name))
                product = result.scalar_one_or_none()
                if product is None or product.icon_or_image_url:
                    skipped += 1
                    continue
                image_path = PRODUCTS_DIR / filename
                if not image_path.exists():
                    print(f"  missing file: {image_path}")
                    failed += 1
                    continue
                try:
                    message = await bot.send_photo(
                        chat_id=settings.seed_factory_telegram_id,
                        photo=FSInputFile(image_path),
                        caption=f"seed: {name}",
                    )
                    product.icon_or_image_url = message.photo[-1].file_id
                    await session.commit()
                    uploaded += 1
                except Exception as exc:  # noqa: BLE001 — best-effort upload, report and continue
                    print(f"  upload failed for {name}: {exc}")
                    failed += 1
        finally:
            await bot.session.close()

        print(f"Photo upload: uploaded={uploaded}, skipped(already set)={skipped}, failed={failed}")
        if failed:
            print(
                "Some uploads failed — make sure SEED_FACTORY_TELEGRAM_ID has pressed /start "
                "on the client bot (@miramaxmpp_bot) at least once, then re-run this script."
            )


if __name__ == "__main__":
    asyncio.run(main())
