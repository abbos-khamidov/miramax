#!/usr/bin/env sh
set -eu

export DATABASE_URL="${BOT_LOCAL_DATABASE_URL:-postgresql+asyncpg://miramax:miramax@127.0.0.1:55432/miramax}"
export DATABASE_URL_SYNC="${BOT_LOCAL_DATABASE_URL_SYNC:-postgresql+psycopg2://miramax:miramax@127.0.0.1:55432/miramax}"

exec .venv/bin/python -m telegram_bot.bot
