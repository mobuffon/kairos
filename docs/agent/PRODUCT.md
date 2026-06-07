# Kairos — product brief (agent summary)
# Full brief: see docs/PRODUCT_BRIEF.md
# This is the condensed version for quick agent reference.

---

## What Kairos is

A personal leisure assistant that monitors conditions (weather, swell, season) and the user's calendar, then proactively suggests — via Telegram — the right leisure activity at the right moment. It learns about the user continuously and adapts its suggestions as their life changes.

## Core loop

```
conditions check + calendar gap → suggestion scored → Telegram message → user confirms → calendar event added
```

Runs twice daily (6am + 4pm) per user, in their timezone.

## The value proposition

Users miss leisure moments they care about not because the opportunity wasn't there, but because they weren't paying attention at the right moment. Kairos pays attention for them.

## What it is not

- Not a life scheduler or productivity tool
- Not a generic assistant (it has a fixed skill library per user's configured activities)
- Not a data harvesting product (the user can see and delete everything Kairos knows)

## Primary user interaction

- **Telegram** — all proactive suggestions, all conversational learning, check-ins
- **Web UI** — Google Calendar OAuth, settings, profile inspection, hobby toggles

## Leisure categories covered

1. Outdoor + nature sports (surf, cycling, hiking, tennis, running, etc.)
2. Fitness and training
3. Social and connection (friend calls, family contact)
4. Culture and entertainment (cinema, concerts, etc.)
5. Learning and growth (reading, instrument, courses)
6. Rest and wellbeing (meditation, walks, etc.)
7. Life planning (trips, bookings, events)

## Learning system

- Onboarding: conversational, not a form
- Ongoing: every inbound message is processed for profile updates
- Check-ins: every 1–2 weeks, a short message asking what's coming up
- Temporary states: injury, travel, busy periods — suppress relevant suggestions with expiry
- User control: "what do you know about me?" + ability to delete any fact

## MVP scope

Activities: surf, cycling, hiking, running, gym, friend/family calls.
Channel: Telegram only.
Calendar: Google Calendar only.
Deployment: Railway.

## Design principles for the agent

1. Suggest less, not more — a missed suggestion is better than an annoying one
2. Be specific — conditions summary must always include the actual numbers
3. Stay quiet when life is clearly disrupted — read active profile facts before scoring
4. One tap to confirm — every suggestion must have inline keyboard buttons
5. The user's profile is always readable and editable — never hide what you know
