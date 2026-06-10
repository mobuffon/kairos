# Kairos — architecture reference
# Agents: read this before writing any code. Update this when you make structural changes.

---

## Stack

| Layer | Technology | Notes |
|---|---|---|
| Backend API | FastAPI (Python 3.12) | Async throughout |
| Task queue / scheduler | APScheduler (embedded) + Redis | APScheduler for MVP; migrate to Celery if user count > 1k |
| Database | PostgreSQL 16 | Primary data store |
| ORM | SQLAlchemy 2.0 (async) | Use `AsyncSession` everywhere |
| Migrations | Alembic | Auto-generate, always review before applying |
| Cache | Redis 7 | Session cache, weather cache, rate limiting |
| LLM | Anthropic Claude API | claude-sonnet-4-20250514 for suggestion generation |
| Frontend | Next.js 14 (App Router) | TypeScript strict mode |
| Bot | python-telegram-bot v21 | Webhook mode (not polling) |
| Auth | JWT + Telegram Login Widget | No username/password |
| Deployment | Docker Compose (local), Railway (prod) | See docker-compose.yml |

---

## Database schema

### Core tables

```sql
users
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid()
  telegram_id     bigint UNIQUE NOT NULL
  telegram_username text
  timezone        text NOT NULL DEFAULT 'UTC'
  location_lat    float
  location_lng    float
  location_label  text                          -- "Lisbon, Portugal"
  quiet_hours_start int DEFAULT 22              -- local hour, 0-23
  quiet_hours_end   int DEFAULT 7
  max_suggestions_per_day int DEFAULT 2
  check_in_frequency_days int DEFAULT 14
  last_check_in_at  timestamptz
  created_at      timestamptz DEFAULT now()
  updated_at      timestamptz DEFAULT now()

user_hobbies
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid()
  user_id         uuid REFERENCES users(id) ON DELETE CASCADE
  hobby_type      text NOT NULL                 -- 'surf' | 'cycling' | 'hiking' | ...
  enabled         boolean DEFAULT true
  config          jsonb NOT NULL DEFAULT '{}'   -- skill-specific thresholds
  created_at      timestamptz DEFAULT now()
  updated_at      timestamptz DEFAULT now()
  UNIQUE(user_id, hobby_type)

user_profile_facts
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid()
  user_id         uuid REFERENCES users(id) ON DELETE CASCADE
  category        text NOT NULL                 -- 'injury' | 'travel' | 'preference' | 'life_event' | ...
  fact            text NOT NULL                 -- human-readable fact
  valid_from      timestamptz DEFAULT now()
  valid_until     timestamptz                   -- null = indefinite
  source          text                          -- 'onboarding' | 'check_in' | 'conversation' | 'inferred'
  created_at      timestamptz DEFAULT now()

user_contacts
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid()
  user_id         uuid REFERENCES users(id) ON DELETE CASCADE
  name            text NOT NULL
  relationship_type text                        -- 'friend' | 'family' | 'colleague'
  contact_frequency_days int DEFAULT 30
  last_contacted_at timestamptz
  notes           text

user_calendars
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid()
  user_id         uuid REFERENCES users(id) ON DELETE CASCADE
  provider        text DEFAULT 'google'
  google_refresh_token text
  calendar_id     text DEFAULT 'primary'
  sync_enabled    boolean DEFAULT true

suggestions
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid()
  user_id         uuid REFERENCES users(id) ON DELETE CASCADE
  hobby_type      text NOT NULL
  window_start    timestamptz NOT NULL
  window_end      timestamptz NOT NULL
  score           float NOT NULL
  conditions_summary text
  message_text    text
  sent_at         timestamptz
  response        text                          -- 'confirmed' | 'dismissed' | 'snoozed' | 'expired'
  responded_at    timestamptz
  calendar_event_id text                        -- Google Calendar event ID if confirmed

conversations
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid()
  user_id         uuid REFERENCES users(id) ON DELETE CASCADE
  direction       text NOT NULL                 -- 'inbound' | 'outbound'
  channel         text NOT NULL                 -- 'telegram' | 'whatsapp'
  message_text    text NOT NULL
  extracted_facts jsonb                         -- facts extracted by the learning agent
  created_at      timestamptz DEFAULT now()
```

### Indexes

```sql
CREATE INDEX idx_user_hobbies_user_id ON user_hobbies(user_id);
CREATE INDEX idx_suggestions_user_id_sent ON suggestions(user_id, sent_at DESC);
CREATE INDEX idx_suggestions_window ON suggestions(window_start, window_end);
CREATE INDEX idx_profile_facts_user_valid ON user_profile_facts(user_id, valid_until);
CREATE INDEX idx_conversations_user_created ON conversations(user_id, created_at DESC);
CREATE INDEX idx_contacts_user_id ON user_contacts(user_id);
```

---

## Key design patterns

### Skill interface
All activity skills inherit from `backend/skills/base.py::BaseSkill`. Never add skill logic outside a skill module. See `.cursor/rules` for the interface definition.

### Profile fact system
The `user_profile_facts` table is the learning layer. Facts have a validity window. The learning agent writes here after every conversation. Examples:

```json
{"category": "injury", "fact": "broken right arm", "valid_until": "2025-09-15"}
{"category": "travel", "fact": "traveling in Japan", "valid_until": "2025-08-10"}
{"category": "preference", "fact": "prefers morning sessions over evening ones", "valid_until": null}
{"category": "life_event", "fact": "started new job, schedule tighter until end of year", "valid_until": "2025-12-31"}
```

The scheduler reads active facts (where `valid_until IS NULL OR valid_until > now()`) and uses them to suppress or adjust suggestions.

### Scheduler job flow

```
APScheduler (every 30 min) →
  for each user where next_run_at <= now():
    1. load_user_context(user_id)         # profile + active facts + hobbies
    2. fetch_calendar_gaps(user_id)       # next 48h free slots
    3. for each enabled hobby:
         fetch_context() → score_windows()
    4. rank_suggestions()                 # sort by score, deduplicate, respect daily limit
    5. if top_score > user.min_threshold:
         generate_message(Claude API)
         send_telegram(message + inline keyboard)
         write suggestions row
    6. update next_run_at (morning/evening cadence in user timezone)
```

### Learning agent flow

```
inbound Telegram message →
  1. store in conversations table
  2. call learning_agent(message, user_context)
     → Claude extracts structured facts
     → returns list of {category, fact, valid_until, action}
       action: 'add' | 'update' | 'delete'
  3. apply facts to user_profile_facts
  4. if action affects active suggestions: suppress or adjust
  5. reply to user confirming any profile changes
```

### Redis key conventions

```
weather:{lat_2dp}:{lng_2dp}:{date}         TTL: 2h    # weather cache
calendar:{user_id}:{date}                  TTL: 30m   # calendar gaps cache
rate_limit:telegram:{user_id}              TTL: 1m    # message rate limit
job_lock:scheduler:{user_id}               TTL: 5m    # prevent double-run
check_in_pending:{user_id}                 TTL: 7d    # pending check-in flag
```

---

## External API dependencies

| API | Purpose | Auth | Rate limit notes |
|---|---|---|---|
| Open-Meteo | Weather forecast | None (free) | 10k calls/day; cache aggressively |
| Open-Meteo Marine | Surf / swell forecast | None (free) | Same quota as above |
| Google Calendar API | Read/write user calendars | OAuth2 per-user | 1M queries/day global; fine |
| Telegram Bot API | Send/receive messages | Bot token | 30 msg/sec global; 1 msg/sec per chat |
| Anthropic Claude API | Suggestion copy + learning agent | API key | Rate limit per tier; add retry logic |

---

## Environment variables

All defined and validated in `backend/core/config.py`. See `.env.example` for the full list. Key variables:

```
DATABASE_URL          # postgresql+asyncpg://...
REDIS_URL             # redis://...
ANTHROPIC_API_KEY     # sk-ant-...
TELEGRAM_BOT_TOKEN    # ...
TELEGRAM_WEBHOOK_SECRET  # random string for webhook validation
GOOGLE_CLIENT_ID      # OAuth client
GOOGLE_CLIENT_SECRET
JWT_SECRET            # random 32-byte string
ENVIRONMENT           # local | staging | production
```

---

## Deployment

Local: `docker-compose up` starts `app`, `postgres`, `redis`, `worker` (scheduler process).

Production (Railway):
- `app` service: FastAPI + bot webhook handler
- `worker` service: APScheduler process (`python -m backend.scheduler.worker`)
- `postgres` and `redis` as Railway managed services

Health check endpoint: `GET /health` → `{"status": "ok", "db": "ok", "redis": "ok"}`
