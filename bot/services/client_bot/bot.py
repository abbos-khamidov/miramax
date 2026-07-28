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
from services.client_bot import handlers
from services.client_bot.middlewares.db import DbSessionMiddleware


async def _set_commands(bot: Bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Botni boshlash"),
            BotCommand(command="menu", description="Mening menyum"),
            BotCommand(command="catalog", description="Katalogni ochish"),
            BotCommand(command="balance", description="Ballarim"),
            BotCommand(command="products", description="Tovarlar"),
            BotCommand(command="search", description="Tovar qidirish"),
            BotCommand(command="history", description="Almashtirish tarixi"),
            BotCommand(command="help", description="Yordam"),
        ]
    )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    dp = Dispatcher(storage=MemoryStorage())

    dp.update.outer_middleware(DbSessionMiddleware())

    dp.include_router(handlers.router)

    while True:
        session = AiohttpSession(proxy=settings.telegram_proxy_url) if settings.telegram_proxy_url else None
        bot = Bot(
            token=settings.bot_token,
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
