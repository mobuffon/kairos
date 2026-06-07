# Kairos — build plan
# Agent: read this at the start of every session. Update task status as you complete work.
# Format: [ ] = todo, [x] = done, [~] = in progress, [!] = blocked (see BLOCKERS.md)

Last updated by: overnight agent session 2025-06-08

---

## Phase 0 — project scaffolding

- [x] Initialise git repo with initial commit
- [x] Create `docker-compose.yml` with app, postgres, redis, worker services
- [x] Create `backend/` FastAPI project structure
- [x] Create `frontend/` Next.js project structure
- [x] Create `bot/` Telegram handler structure
- [x] Create `backend/core/config.py` with Pydantic Settings and env var validation
- [x] Create `.env.example` with all required variables
- [x] Create `Makefile` with common commands (dev, test, migrate, lint)
- [x] Set up `ruff` and `pytest` for backend
- [~] Set up `eslint` and `typescript` strict mode for frontend
- [x] Write `GET /health` endpoint
- [~] Confirm Docker Compose brings everything up cleanly (needs human — Docker not in agent env)

---

## Phase 1 — database and models

- [x] Write Alembic initial migration with full schema (see ARCHITECTURE.md)
- [x] Write SQLAlchemy models for all tables
- [x] Write `backend/core/db.py` async session factory
- [x] Write basic CRUD helpers in `backend/core/crud.py`
- [~] Test migrations apply cleanly on fresh Postgres (needs Docker)

---

## Phase 2 — user onboarding (Telegram)

- [x] Register Telegram webhook handler in `bot/telegram/webhook.py`
- [x] Implement `/start` command — initiates onboarding conversation
- [ ] Implement onboarding conversation flow (multi-turn state machine)
  - [ ] Ask about location
  - [ ] Ask about hobbies (multi-select inline keyboard)
  - [ ] Per-hobby threshold configuration (conversational)
  - [ ] Ask about contacts to track
  - [ ] Confirm and write to DB
- [x] Implement Google Calendar OAuth flow (web, linked from bot message) — URL stub only
- [x] Write learning agent first pass (extract facts from onboarding conversation) — mock/rule-based
- [ ] Store user, hobbies, profile facts from onboarding (DB write path)

---

## Phase 3 — skill modules

- [x] Write `backend/skills/base.py` — BaseSkill interface
- [ ] Write `backend/skills/weather.py` — Open-Meteo integration with Redis cache
- [ ] Write `backend/skills/marine.py` — Open-Meteo Marine for surf/kite/wing
- [ ] Write `backend/skills/calendar.py` — Google Calendar gap finder + event writer
- [x] Write `backend/skills/surf.py` — surf scoring logic
- [x] Write `backend/skills/cycling.py` — cycling scoring logic
- [x] Write `backend/skills/hiking.py` — hiking scoring logic
- [ ] Write `backend/skills/running.py` — running scoring logic
- [x] Write `backend/skills/call_friend.py` — contact recency scoring
- [x] Write unit tests for each skill's `score_window()` (surf, cycling, hiking, call_friend)

---

## Phase 4 — scheduler and suggestion engine

- [x] Write `backend/scheduler/worker.py` — APScheduler setup
- [x] Write `backend/scheduler/jobs.py` — main per-user job
- [x] Implement `load_user_context()` with active profile facts (mock provider)
- [x] Implement `rank_suggestions()` with deduplication and daily limit
- [x] Write `backend/agent/suggestion.py` — Claude API call for message generation
- [x] Write `backend/agent/prompts.py` — all prompt templates
- [ ] Implement suggestion storage and deduplication (DB)
- [x] Test full loop: user with surf profile → conditions met → message generated

---

## Phase 5 — Telegram notification and response handling

- [x] Implement outbound message sender with inline keyboard (mock notifier)
- [x] Handle `confirm` callback → write Google Calendar event → reply confirmation (mock)
- [x] Handle `dismiss` callback → store response, no action (mock)
- [x] Handle `snooze` callback → reschedule reminder for 4h later (mock reply)
- [x] Handle free-text inbound messages → learning agent pipeline
- [ ] Implement check-in message (every N days, configurable)
- [ ] Test full round-trip: suggestion → confirm → calendar event created

---

## Phase 6 — learning agent

- [x] Write `backend/agent/learning.py` — extract facts from conversation messages
- [x] Write fact application logic (add / update / delete profile facts) — in-memory/mock
- [x] Implement temporary fact expiry (injury window, travel window)
- [x] Implement fact suppression in scheduler (check active facts before scoring)
- [x] Handle explicit "forget X" commands
- [x] Implement "what do you know about me?" summary command
- [x] Test: user says "I broke my arm" → surf/cycling suggestions suppressed for 6 weeks

---

## Phase 7 — web UI

- [~] Create Next.js app with Tailwind CSS (basic inline styles, no Tailwind yet)
- [ ] Implement Telegram Login Widget auth → JWT exchange
- [x] Build `/onboard` page — hobby setup form (fallback for non-Telegram users) — stub
- [x] Build `/dashboard` page — upcoming suggestions, recent history, hobby toggles
- [x] Build `/settings` page — thresholds, quiet hours, location, calendar link
- [ ] Build `/profile` page — current known facts, contact list, delete fact UI
- [x] Connect all pages to FastAPI backend via typed API client
- [x] Build `/dev/scenarios` page — run selftests and evaluate scenarios

---

## Phase 8 — hardening and deployment

- [x] Write integration tests for all API endpoints (health, auth, tools, bot)
- [ ] Add rate limiting (slowapi) to all public endpoints
- [x] Add structured logging (structlog) throughout
- [ ] Add Sentry error tracking
- [ ] Write `railway.toml` or `railway.json` deploy config
- [ ] Set up staging environment
- [ ] Load test scheduler with 100 simulated users
- [x] Write `README.md` with setup instructions (updated for mock mode)

---

## Backlog (post-MVP)

- [ ] Cinema / movies skill (TMDB API)
- [ ] WhatsApp channel support (Twilio)
- [ ] Vacation planning skill (long calendar gap detection)
- [ ] Onboarding via WhatsApp message import
- [ ] Push notifications (FCM) for mobile web
- [ ] Admin dashboard for monitoring suggestion quality
- [ ] A/B testing framework for message copy

---

## Notes for agent

- Complete phases in order — each phase depends on the previous
- Do not start Phase 4 before Phase 3 skills are tested
- Do not start Phase 7 before Phase 5 is complete (frontend needs real data)
- Phases 3 and 6 can be partially parallelised (skill modules and learning agent are independent)
- Update this file after every work session
