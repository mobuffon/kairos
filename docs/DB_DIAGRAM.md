# Kairos — Database ER Diagram

PostgreSQL 16 schema (Alembic revision `001_initial`). All `user_id` foreign keys cascade on delete.

```mermaid
erDiagram
    users ||--o{ user_hobbies : "has"
    users ||--o{ user_profile_facts : "has"
    users ||--o{ user_contacts : "has"
    users ||--o{ user_calendars : "has"
    users ||--o{ suggestions : "receives"
    users ||--o{ conversations : "has"

    users {
        uuid id PK
        bigint telegram_id UK "NOT NULL"
        text telegram_username
        text timezone "NOT NULL, default UTC"
        float location_lat
        float location_lng
        text location_label
        int quiet_hours_start "default 22"
        int quiet_hours_end "default 7"
        int max_suggestions_per_day "default 2"
        int check_in_frequency_days "default 14"
        timestamptz last_check_in_at
        timestamptz created_at
        timestamptz updated_at
    }

    user_hobbies {
        uuid id PK
        uuid user_id FK "NOT NULL"
        text hobby_type "NOT NULL"
        boolean enabled "default true"
        jsonb config "NOT NULL, default {}"
        timestamptz created_at
        timestamptz updated_at
    }

    user_profile_facts {
        uuid id PK
        uuid user_id FK "NOT NULL"
        text category "NOT NULL"
        text fact "NOT NULL"
        timestamptz valid_from
        timestamptz valid_until "null = indefinite"
        text source
        timestamptz created_at
    }

    user_contacts {
        uuid id PK
        uuid user_id FK "NOT NULL"
        text name "NOT NULL"
        text relationship_type
        int contact_frequency_days "default 30"
        timestamptz last_contacted_at
        text notes
    }

    user_calendars {
        uuid id PK
        uuid user_id FK "NOT NULL"
        text provider "default google"
        text google_refresh_token
        text calendar_id "default primary"
        boolean sync_enabled "default true"
    }

    suggestions {
        uuid id PK
        uuid user_id FK "NOT NULL"
        text hobby_type "NOT NULL"
        timestamptz window_start "NOT NULL"
        timestamptz window_end "NOT NULL"
        float score "NOT NULL"
        text conditions_summary
        text message_text
        timestamptz sent_at
        text response
        timestamptz responded_at
        text calendar_event_id "Google event ID"
    }

    conversations {
        uuid id PK
        uuid user_id FK "NOT NULL"
        text direction "NOT NULL inbound or outbound"
        text channel "NOT NULL telegram or whatsapp"
        text message_text "NOT NULL"
        jsonb extracted_facts
        timestamptz created_at
    }
```

## Relationships

| Parent | Child | Cardinality | Notes |
|--------|-------|-------------|-------|
| `users` | `user_hobbies` | 1 : 0..N | `UNIQUE(user_id, hobby_type)` |
| `users` | `user_profile_facts` | 1 : 0..N | Learning layer; validity windows |
| `users` | `user_contacts` | 1 : 0..N | Social/contact tracking |
| `users` | `user_calendars` | 1 : 0..N | OAuth calendar connections |
| `users` | `suggestions` | 1 : 0..N | Proactive activity suggestions |
| `users` | `conversations` | 1 : 0..N | Message log |

## Logical flows

- **Scheduler** reads `users`, `user_hobbies`, `user_profile_facts`, `user_calendars` → writes `suggestions`
- **Learning agent** reads/writes `conversations` → extracts facts into `user_profile_facts`
- **`suggestions.calendar_event_id`** stores a Google Calendar event ID (not an FK)
