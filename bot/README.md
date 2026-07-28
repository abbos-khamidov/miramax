# Miramax Bonus — Bot (Phase 1: Завод + Поставщик)

Greenfield bonus-program backend + Telegram bot + Mini App for Miramax. Chain: Завод → Поставщик → Магазин → Продавец → Покупатель. This phase covers the Factory (read-only analytics) and Supplier (store/invite management) roles only.

## Stack

- **Backend**: FastAPI + SQLAlchemy (async, asyncpg) + Alembic — `services/backend/`, `core/`
- **Bots**: aiogram 3 (long polling), three independent bots (own token, own container) — `services/client_bot/`, `services/admin_bot/`, `services/seller_bot/`
- **Mini App**: Vite + React + Tailwind (design tokens and UI primitives reused from `../mvp/first version`) — `miniapp/`
- **DB**: PostgreSQL

`core/` holds the shared models and business logic; `services/backend/` (HTTP API for the Mini App) and all three bots under `services/` call into it directly — no HTTP hop between a bot and its own backend.

### Layout of `services/`

Each subfolder is a self-contained deployable unit (own entrypoint, own `keyboards.py`/`states.py`, own `middlewares/`) — changing one doesn't touch the others, and each has its own `docker compose` service so it can be rebuilt/restarted/deployed independently:

- `client_bot/` — customer-facing bot (`BOT_TOKEN`): catalog, balance, redemption history.
- `admin_bot/` — factory-only bot (`ADMIN_BOT_TOKEN`), fully isolated: add suppliers, network-wide analytics.
- `seller_bot/` — supplier + seller bot (`SELLER_BOT_TOKEN`), role-routed inside: manage stores/invites (supplier), record sales (seller).
- `backend/` — FastAPI HTTP API backing the Mini Apps.

## Local setup

1. `cp .env.example .env` and fill in `BOT_TOKEN`/`BOT_USERNAME`, `ADMIN_BOT_TOKEN`/`ADMIN_BOT_USERNAME`, `SELLER_BOT_TOKEN`/`SELLER_BOT_USERNAME` (each from @BotFather) — the `*_USERNAME` values matter now: invite links are built per target role (customer → client bot, supplier/wholesaler/seller → seller bot, admin → admin bot), so a wrong username sends people to the wrong bot.
2. `cp miniapp/.env.example miniapp/.env` (defaults are fine — leave `VITE_API_BASE_URL` unset).
3. `docker compose up --build` — starts Postgres, runs Alembic migrations, then starts the backend (`:8000`), the bot (long polling), and the Mini App dev server (`:5173`), all in one command.
4. Seed the first factory + supplier accounts (edit `SEED_FACTORY_TELEGRAM_ID` / `SEED_SUPPLIER_TELEGRAM_ID` in `.env` to your real Telegram user IDs first):
   ```
   docker compose exec backend python seed.py
   ```
   There is no admin UI in this phase — role assignment is manual, by design (see the phase-1 spec).

## Testing the Mini App inside Telegram

Telegram only opens WebApp URLs over HTTPS, so `http://localhost:5173` won't work from inside the Telegram client. During local dev, tunnel just the Mini App:

```
ngrok http 5173
```

Set `MINIAPP_URL` in `.env` to the resulting `https://...ngrok-free.app` URL and restart the `bot` service. The Mini App's own API calls go through Vite's `/api` proxy to the `backend` container, so **one tunnel is enough** — the backend does not need its own public URL for local testing. Once deployed to a VPS, both are served from the same domain via a reverse proxy, and this proxy config is replaced accordingly.

## Verifying end-to-end

1. Message the bot from the seeded supplier account → menu appears → "Добавить магазин" → create 2–3 stores → "Мои магазины" lists them.
2. "Пригласить продавца" on a store → open the returned link from a third Telegram account → confirmation message, and that account is now bound to the store as a seller (`roles` table).
3. Message the bot from the seeded factory account → "Открыть аналитику" button opens the Mini App → shows the supplier and its stores with zero sales (real structure, no sales data yet — out of scope for this phase).
4. `GET /api/analytics/factory` and `GET /api/suppliers/{id}/stores` can be called directly with a valid Telegram `initData` header for spot-checking the API.

## Scope notes

- No sales/transactions tables exist yet — analytics show real supplier/store structure with sales metrics stubbed at zero until phase 2 wires up actual sales.
- Seller role redemption via invite link only binds the account to a store; the seller's own bonus-earning menu is phase 2.
- `factory` role has no separate "factory" entity — it's treated as a single global viewer over the whole network. If multi-factory ever becomes a requirement, the schema will need a `factories` table.
- Wholesaler (`Supplier.kind = wholesaler`) is purely a label for Factory-side bookkeeping — it behaves identically to a supplier in `seller_bot` (same role, same menu, same permissions). Split it into a real `RoleName.WHOLESALER` only if its seller_bot behavior ever needs to diverge.
- `admin_bot` supports self-service admin onboarding (Factory can add another Admin via the same QR-invite flow as Supplier/Wholesaler) and RU/UZ/TR language selection (stored per-`Role` in `roles.language`, prompted on first `/start`). This is not yet extended to `client_bot`/`seller_bot`.
- `uz`/`tr` copy in `services/admin_bot/i18n.py` is a first-pass translation, not reviewed by a native speaker — worth a proofread pass before relying on it in production.
