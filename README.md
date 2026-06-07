# Kairos

A personal leisure assistant that monitors conditions and your calendar, then tells you when the right moment for something you love is about to happen.

Full product brief: `docs/PRODUCT_BRIEF.md`

---

## Quick start

```bash
# 1. Clone and configure
cp .env.example .env
# Fill in ANTHROPIC_API_KEY, TELEGRAM_BOT_TOKEN, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

# 2. Start all services
make dev

# 3. Run migrations
make migrate

# 4. Register Telegram webhook (after deploying or using ngrok locally)
curl -X POST https://api.telegram.org/bot<TOKEN>/setWebhook \
  -d url=https://your-domain.com/bot/webhook \
  -d secret_token=<TELEGRAM_WEBHOOK_SECRET>
```

Then open `http://localhost:3000` for the web UI, or message your bot on Telegram.

---

## Project structure

```
backend/      FastAPI app + scheduler worker
frontend/     Next.js web UI
bot/          Telegram webhook handler
tests/        Unit and integration tests
docs/agent/   Agent-readable documentation (PLAN, ARCHITECTURE, DECISIONS)
migrations/   Alembic database migrations
```

## Common commands

```bash
make dev          # start everything with hot reload
make test         # run all tests
make lint         # check code style
make migrate      # apply pending migrations
make migrate-create  # create a new migration
make logs         # tail app and worker logs
make psql         # open postgres shell
```

## For AI coding agents

Read `CLAUDE.md` (Claude) or `.cursor/rules` (Cursor) before doing anything. Then read `docs/agent/PLAN.md` for current task state.

---

## Tech stack

- **Backend:** FastAPI, SQLAlchemy (async), Alembic, APScheduler
- **Frontend:** Next.js 14, TypeScript, Tailwind CSS
- **Bot:** python-telegram-bot v21
- **Database:** PostgreSQL 16
- **Cache/Queue:** Redis 7
- **LLM:** Anthropic Claude API
- **Deploy:** Docker Compose (local), Railway (production)
