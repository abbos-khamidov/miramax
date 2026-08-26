import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from core.config import settings
from services.seller_bot.handlers import issue_points, seller, start, supplier
from services.seller_bot.middlewares.db import DbSessionMiddleware


async def _set_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Открыть меню"),
            BotCommand(command="help", description="Инструкция"),
        ]
    )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    dp = Dispatcher(storage=MemoryStorage())

    dp.update.outer_middleware(DbSessionMiddleware())

    dp.include_router(start.router)
    dp.include_router(supplier.router)
    dp.include_router(seller.router)
    dp.include_router(issue_points.router)

    while True:
        session = AiohttpSession(proxy=settings.telegram_proxy_url) if settings.telegram_proxy_url else None
        bot = Bot(
            token=settings.seller_bot_token,
            session=session,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        try:
            await bot.delete_webhook(drop_pending_updates=True, request_timeout=120)
            await _set_commands(bot)
            await dp.start_polling(bot)
            break
        except TelegramNetworkError as exc:
            logger.warning("Telegram API is unavailable, retrying in 15 seconds: %s", exc)
            await bot.session.close()
            await asyncio.sleep(15)
        except Exception:
            await bot.session.close()
            raise


if __name__ == "__main__":
    asyncio.run(main())
