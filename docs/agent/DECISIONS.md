# Kairos — decision log
# Agent: log every significant decision here with reasoning. Read this before making similar decisions.
# Format: newest entries at the top.

---

## Template

### [YYYY-MM-DD] Title of decision

**Context:** What situation prompted this decision?
**Options considered:** What alternatives existed?
**Decision:** What was chosen?
**Reasoning:** Why?
**Consequences:** What does this constrain or enable going forward?

---

## Decisions

### [2025-06-08] MOCK_EXTERNAL_APIS with placeholder secret detection

**Context:** Overnight build must run without Telegram, Google, or Anthropic credentials.
**Options considered:** (a) Require all secrets upfront. (b) Separate mock flag per provider. (c) Global `MOCK_EXTERNAL_APIS` plus treat `.env.example` placeholders as unset.
**Decision:** `MOCK_EXTERNAL_APIS=true` default + `_is_real_secret()` rejects `...` and template values.
**Reasoning:** Developers can copy `.env.example` and work immediately. Real tokens opt in by setting non-placeholder values and `MOCK_EXTERNAL_APIS=false`.
**Consequences:** All provider selection goes through `Settings.use_mock_*` properties. Never check raw env strings for "is configured".

---

### [2025-06-08] Mock Telegram notifier logs to JSONL file

**Context:** Outbound messages can't be sent without a bot token.
**Options considered:** (a) Skip send silently. (b) Log to stdout only. (c) Append to `data/mock_notifications.jsonl`.
**Decision:** JSONL file in `data/` (gitignored).
**Reasoning:** Inspectable audit trail for dev and integration tests; mirrors what would be sent to Telegram.
**Consequences:** Production must use real `send_message` path when `use_mock_telegram` is false.

---

### [2025-06-08] Rule-based learning agent as LLM fallback

**Context:** No Anthropic key during unattended build.
**Options considered:** (a) Skip learning agent. (b) Hard-code a few test cases only. (c) Regex/keyword extraction with same `ExtractedFact` schema as Claude path.
**Decision:** Keyword extraction for injury, travel, preferences, and "forget X" commands.
**Reasoning:** Exercises the full pipeline (extract → apply → suppress) without API cost. Claude path remains for production.
**Consequences:** Add new patterns to `extract_facts_mock()` when selftest scenarios need them.

---

### [2025-06-08] APScheduler chosen over Celery for MVP scheduler

**Context:** Need a background job system to run per-user suggestion checks on a schedule.
**Options considered:** Celery + Redis Beat (distributed, proven at scale), APScheduler (embedded, simpler), Temporal (complex, overkill for MVP).
**Decision:** APScheduler embedded in a dedicated worker process.
**Reasoning:** Celery adds significant operational complexity (separate beat scheduler process, result backend, task serialisation). For an MVP with < 1,000 users, APScheduler running in-process is sufficient and far simpler to deploy. The scheduler logic is already async; APScheduler's AsyncScheduler integrates cleanly.
**Consequences:** If user count exceeds ~5,000 concurrent users with active schedules, we should migrate to Celery. The job logic is isolated in `backend/scheduler/jobs.py` and should be portable. Do not couple any business logic to APScheduler-specific APIs.

---

### [2025-06-08] Profile facts stored as rows, not as JSONB blob on user

**Context:** Designing how to store learned facts about users (injuries, travel, preferences).
**Options considered:** (a) Single JSONB column on `users` table updated in place. (b) Separate `user_profile_facts` table with one row per fact.
**Decision:** Separate `user_profile_facts` table.
**Reasoning:** Facts need validity windows (`valid_from`, `valid_until`), provenance (`source`), and the ability to be individually deleted without affecting others. A JSONB blob makes querying active facts, expiring temporary facts, and auditing changes much harder. Row-per-fact also makes it easy to show the user "here's everything I know about you" as a readable list.
**Consequences:** Slightly more complex queries, but the tradeoff is worth it. Always query active facts with `WHERE valid_until IS NULL OR valid_until > now()`.

---

### [2025-06-08] Telegram as primary channel, web as secondary

**Context:** Choosing the primary user interaction surface for MVP.
**Options considered:** Native mobile app, web app, Telegram bot, WhatsApp.
**Decision:** Telegram bot as primary, minimal web UI for settings only.
**Reasoning:** Telegram provides push notification delivery, inline keyboards for one-tap responses, and no app store approval process. Web handles the OAuth flows (Google Calendar) and complex settings that are awkward in a chat interface. WhatsApp is a near-term addition but requires a business account review process.
**Consequences:** All suggestion delivery and conversational learning must work entirely through Telegram. The web UI is a complement, not a parallel channel — users who never visit the web UI must still have a full experience.

---

### [2025-06-08] Open-Meteo chosen for weather (free tier)

**Context:** Need a weather API for hourly forecast data including marine conditions.
**Options considered:** OpenWeatherMap (free tier rate limited), Tomorrow.io (generous free tier, commercial), Open-Meteo (fully free, open source), WeatherAPI.
**Decision:** Open-Meteo for both standard weather and marine forecast.
**Reasoning:** No API key required, no rate limit concerns for MVP scale, hourly resolution is sufficient, marine endpoint covers swell height and period for surf scoring. Commercial APIs add cost and key management overhead unnecessarily at this stage.
**Consequences:** If we need features like hyperlocal radar, UV index confidence intervals, or real-time lightning data, we may need to supplement with a commercial API later. Cache all Open-Meteo responses in Redis with a 2h TTL to stay comfortably within the 10k/day limit.
