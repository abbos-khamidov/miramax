from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError

from core.config import settings


async def notify_customer(telegram_id: int, text: str) -> None:
    """Best-effort push to a customer's chat with the client bot — used when a seller
    records a sale for them elsewhere (seller_bot has no chat of its own with them).
    Failures (blocked bot, chat not found, etc.) are swallowed: the seller already got
    their own confirmation, and this is a nice-to-have on top of it."""
    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    try:
        await bot.send_message(chat_id=telegram_id, text=text)
    except TelegramAPIError:
        pass
    finally:
        await bot.session.close()
