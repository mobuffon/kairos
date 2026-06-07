# Blockers
# Agent: write here when unattended execution hits something that cannot proceed without human input.
# Format: newest at top. Remove entries once resolved.

Status: 3 items need human secrets (see below). All other work continues in mock mode.

---

### [2025-06-08] External API credentials

**Task affected:** Phase 2 (Telegram onboarding), Phase 5 (notifications), Google Calendar OAuth
**What I tried:** Built full mock paths — webhook handler, mock notifier, OAuth URL stub, rule-based LLM
**What I need:**
- `TELEGRAM_BOT_TOKEN` from [@BotFather](https://t.me/BotFather)
- `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` from Google Cloud Console (Calendar API enabled)
- `ANTHROPIC_API_KEY` (optional — mock LLM works without it)
**Work completed so far:** Mock mode fully functional; set `MOCK_EXTERNAL_APIS=true` to develop offline
**Resumption point:** Add tokens to `.env`, set `MOCK_EXTERNAL_APIS=false`, test webhook with ngrok

---

### [2025-06-08] Docker unavailable in cloud agent environment

**Task affected:** Phase 0 docker-compose verification, migration apply on live Postgres
**What I tried:** `docker` / `docker compose` not found in agent shell; tests run via local venv instead
**What I need:** Run `docker compose up --build -d && make migrate` on your machine
**Work completed so far:** All pytest passes without Docker; compose file and migrations unchanged
**Resumption point:** Confirm `GET /health` returns `db: ok, redis: ok` after compose up
