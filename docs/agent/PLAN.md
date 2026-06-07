# Kairos — build plan
# Agent: read this at the start of every session. Update task status as you complete work.
# Format: [ ] = todo, [x] = done, [~] = in progress, [!] = blocked (see BLOCKERS.md)

Last updated by: (agent updates this line with each session)

---

## Phase 0 — project scaffolding

- [ ] Initialise git repo with initial commit
- [ ] Create `docker-compose.yml` with app, postgres, redis, worker services
- [ ] Create `backend/` FastAPI project structure
- [ ] Create `frontend/` Next.js project structure
- [ ] Create `bot/` Telegram handler structure
- [ ] Create `backend/core/config.py` with Pydantic Settings and env var validation
- [ ] Create `.env.example` with all required variables
- [ ] Create `Makefile` with common commands (dev, test, migrate, lint)
- [ ] Set up `ruff` and `pytest` for backend
- [ ] Set up `eslint` and `typescript` strict mode for frontend
- [ ] Write `GET /health` endpoint
- [ ] Confirm Docker Compose brings everything up cleanly

---

## Phase 1 — database and models

- [ ] Write Alembic initial migration with full schema (see ARCHITECTURE.md)
- [ ] Write SQLAlchemy models for all tables
- [ ] Write `backend/core/db.py` async session factory
- [ ] Write basic CRUD helpers in `backend/core/crud.py`
- [ ] Test migrations apply cleanly on fresh Postgres

---

## Phase 2 — user onboarding (Telegram)

- [ ] Register Telegram webhook handler in `bot/telegram/webhook.py`
- [ ] Implement `/start` command — initiates onboarding conversation
- [ ] Implement onboarding conversation flow (multi-turn state machine)
  - [ ] Ask about location
  - [ ] Ask about hobbies (multi-select inline keyboard)
  - [ ] Per-hobby threshold configuration (conversational)
  - [ ] Ask about contacts to track
  - [ ] Confirm and write to DB
- [ ] Implement Google Calendar OAuth flow (web, linked from bot message)
- [ ] Write learning agent first pass (extract facts from onboarding conversation)
- [ ] Store user, hobbies, profile facts from onboarding

---

## Phase 3 — skill modules

- [ ] Write `backend/skills/base.py` — BaseSkill interface
- [ ] Write `backend/skills/weather.py` — Open-Meteo integration with Redis cache
- [ ] Write `backend/skills/marine.py` — Open-Meteo Marine for surf/kite/wing
- [ ] Write `backend/skills/calendar.py` — Google Calendar gap finder + event writer
- [ ] Write `backend/skills/surf.py` — surf scoring logic
- [ ] Write `backend/skills/cycling.py` — cycling scoring logic
- [ ] Write `backend/skills/hiking.py` — hiking scoring logic
- [ ] Write `backend/skills/running.py` — running scoring logic
- [ ] Write `backend/skills/call_friend.py` — contact recency scoring
- [ ] Write unit tests for each skill's `score_window()`

---

## Phase 4 — scheduler and suggestion engine

- [ ] Write `backend/scheduler/worker.py` — APScheduler setup
- [ ] Write `backend/scheduler/jobs.py` — main per-user job
- [ ] Implement `load_user_context()` with active profile facts
- [ ] Implement `rank_suggestions()` with deduplication and daily limit
- [ ] Write `backend/agent/suggestion.py` — Claude API call for message generation
- [ ] Write `backend/agent/prompts.py` — all prompt templates
- [ ] Implement suggestion storage and deduplication
- [ ] Test full loop: user with surf profile → conditions met → message generated

---

## Phase 5 — Telegram notification and response handling

- [ ] Implement outbound message sender with inline keyboard
- [ ] Handle `confirm` callback → write Google Calendar event → reply confirmation
- [ ] Handle `dismiss` callback → store response, no action
- [ ] Handle `snooze` callback → reschedule reminder for 4h later
- [ ] Handle free-text inbound messages → learning agent pipeline
- [ ] Implement check-in message (every N days, configurable)
- [ ] Test full round-trip: suggestion → confirm → calendar event created

---

## Phase 6 — learning agent

- [ ] Write `backend/agent/learning.py` — extract facts from conversation messages
- [ ] Write fact application logic (add / update / delete profile facts)
- [ ] Implement temporary fact expiry (injury window, travel window)
- [ ] Implement fact suppression in scheduler (check active facts before scoring)
- [ ] Handle explicit "forget X" commands
- [ ] Implement "what do you know about me?" summary command
- [ ] Test: user says "I broke my arm" → surf/cycling suggestions suppressed for 6 weeks

---

## Phase 7 — web UI

- [ ] Create Next.js app with Tailwind CSS
- [ ] Implement Telegram Login Widget auth → JWT exchange
- [ ] Build `/onboard` page — hobby setup form (fallback for non-Telegram users)
- [ ] Build `/dashboard` page — upcoming suggestions, recent history, hobby toggles
- [ ] Build `/settings` page — thresholds, quiet hours, location, calendar link
- [ ] Build `/profile` page — current known facts, contact list, delete fact UI
- [ ] Connect all pages to FastAPI backend via typed API client

---

## Phase 8 — hardening and deployment

- [ ] Write integration tests for all API endpoints
- [ ] Add rate limiting (slowapi) to all public endpoints
- [ ] Add structured logging (structlog) throughout
- [ ] Add Sentry error tracking
- [ ] Write `railway.toml` or `railway.json` deploy config
- [ ] Set up staging environment
- [ ] Load test scheduler with 100 simulated users
- [ ] Write `README.md` with setup instructions

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
