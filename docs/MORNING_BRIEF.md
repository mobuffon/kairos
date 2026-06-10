# Kairos — morning brief (2025-06-08)

## Done overnight
- Fixed selftest scenarios path (`tests/selftest/scenarios.yaml`) — 8/8 scenarios pass
- Added hiking skill with unit tests, mock fixtures, and selftest scenario
- Built learning agent skeleton with rule-based extraction (injury, travel, forget)
- Hardened `rank_suggestions` (diversity, dedup) and profile fact suppression with expiry
- Added `MOCK_EXTERNAL_APIS` + placeholder detection for offline dev
- Structured Telegram webhook (`/bot/webhook`) with mock notifier logging to `data/`
- Google Calendar OAuth URL stub at `GET /auth/google/url`
- Frontend: settings page (calendar link, dev users), dev/scenarios page with selftest runner
- Structured logging via structlog; `.cursor/environment.json` for cloud agents

## Working now (how to try)
```bash
cd kairos-scaffold
cp .env.example .env   # MOCK_EXTERNAL_APIS=true by default
python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
pytest tests/ -v
python -m backend.cli selftest
python -m backend.cli evaluate --user darian --mock --scenario darian_hiking_sunny
uvicorn backend.main:app --reload   # then open http://localhost:3000/dev/scenarios
```

## Test results
- **pytest:** 24/24 passed (unit, integration, selftest)
- **YAML scenarios:** 8/8 passed (surf, cycling, hiking, call_friend, injury suppression)
- **Docker:** not run in agent environment — run `docker compose up --build -d && make migrate` locally

## Blocked on you
- `TELEGRAM_BOT_TOKEN` — needed for real outbound messages (mock logs to `data/mock_notifications.jsonl` until set)
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` — needed for real calendar sync (mock provider works now)
- `ANTHROPIC_API_KEY` or `OPENROUTER_API_KEY` — optional; set `LLM_PROVIDER=anthropic|openrouter` in `.env` (rule-based mock fallback when unset)

## Recommended next steps (priority order)
1. Run `docker compose up --build -d && make migrate` and confirm health endpoint shows db/redis ok
2. Add Telegram bot token and test full webhook round-trip with ngrok
3. Implement Google OAuth callback and real calendar gap provider
4. Wire learning agent to DB (`user_profile_facts` + `conversations` tables)
5. Complete onboarding conversation flow in Telegram (`/start` multi-turn)
6. Add running skill and Open-Meteo weather/marine providers (with Redis cache)
7. Deploy staging on Railway with env vars from `.env.example`
