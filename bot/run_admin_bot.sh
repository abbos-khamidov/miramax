#!/bin/sh
# Run the admin/factory bot on the host (not in Docker), pointed at the
# Postgres port published to localhost instead of the in-Docker "db" hostname.
cd "$(dirname "$0")"
export DATABASE_URL="postgresql+asyncpg://miramax:miramax@localhost:55432/miramax"
export DATABASE_URL_SYNC="postgresql+psycopg2://miramax:miramax@localhost:55432/miramax"
exec .venv/bin/python -m services.admin_bot.bot
