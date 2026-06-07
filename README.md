# Kairos

A personal leisure assistant that monitors conditions and your calendar, then tells you when the right moment for something you love is about to happen.

Full product brief: `docs/PRODUCT_BRIEF.md`

---

## Quick start (mock mode — no API keys needed)

```bash
cp .env.example .env          # MOCK_EXTERNAL_APIS=true by default
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

pytest tests/ -v
python -m backend.cli selftest
python -m backend.cli evaluate --user mo --mock --scenario mo_surf_perfect
uvicorn backend.main:app --reload
```

Open `http://localhost:3000` for the web UI, or `http://localhost:3000/dev/scenarios` to run evaluation scenarios.

---

## Full stack (Docker)

```bash
cp .env.example .env
# Optionally fill in ANTHROPIC_API_KEY, TELEGRAM_BOT_TOKEN, GOOGLE_CLIENT_ID

docker compose up --build -d
make migrate
make test
```

Then open `http://localhost:3000` for the web UI.

Register Telegram webhook (after deploying or using ngrok):

```bash
curl -X POST https://api.telegram.org/bot<TOKEN>/setWebhook \
  -d url=https://your-domain.com/bot/webhook \
  -d secret_token=<TELEGRAM_WEBHOOK_SECRET>
```

---

## Mock mode

Set `MOCK_EXTERNAL_APIS=true` in `.env` to run without external services:

| Service | Mock behaviour |
|---|---|
| Anthropic | Rule-based message generation and fact extraction |
| Telegram | Webhook works; outbound messages logged to `data/mock_notifications.jsonl` |
| Google Calendar | OAuth URL returns mock link; gaps from YAML fixtures |

Placeholder values in `.env` (`...`, `sk-ant-...`) are treated as unset.

---

## Project structure

```
backend/      FastAPI app + scheduler worker
frontend/     Next.js web UI
bot/          Telegram webhook handler and mock notifier
tests/        Unit, integration, and YAML selftest scenarios
docs/agent/   Agent-readable documentation (PLAN, ARCHITECTURE, DECISIONS)
migrations/   Alembic database migrations
```

## Common commands

```bash
make dev          # start everything with hot reload (Docker)
make test         # run all tests
make lint         # check code style
make migrate      # apply pending migrations
make logs         # tail app and worker logs
```

## CLI

```bash
python -m backend.cli evaluate --user mo --mock --scenario mo_surf_perfect
python -m backend.cli selftest
```

## For AI coding agents

Read `CLAUDE.md` (Claude) or `.cursor/rules` (Cursor) before doing anything. Then read `docs/agent/PLAN.md` for current task state. Cloud agent setup: `.cursor/environment.json`.

---

## Tech stack

- **Backend:** FastAPI, SQLAlchemy (async), Alembic, APScheduler
- **Frontend:** Next.js 14, TypeScript
- **Bot:** Telegram webhook (python-telegram-bot patterns)
- **Database:** PostgreSQL 16
- **Cache/Queue:** Redis 7
- **LLM:** Anthropic Claude API (optional — mock fallback built in)
- **Deploy:** Docker Compose (local), Railway (production)
