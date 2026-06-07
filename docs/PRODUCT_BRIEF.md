# Kairos — product brief

---

## The problem

Modern life is extraordinarily good at filling time. Work expands, notifications multiply, and the path of least resistance at the end of a long day is the couch and a screen. This is not a failure of willpower or ambition. It is a coordination problem.

Most people know exactly what they love to do. They know a long bike ride on a clear morning makes their week better. They know they feel guilty when months pass without calling their grandmother. They know that a perfect swell only lines up a handful of times a year, and they've missed the last three because they found out too late or were already committed to something forgettable. They know that hiking that trail before winter closes it would have been the best afternoon of the autumn — but they never got around to planning it.

The gap is not desire. The gap is activation energy and timing. Leisure, unlike work, rarely comes with deadlines or reminders. A good surf window doesn't send you a calendar invite. A cinema isn't going to text you that the one film you'd have loved is leaving next week. Your college friend doesn't schedule himself into your week. These things require you to be paying attention at the right moment — to check the forecast on the right morning, to notice a gap in your calendar, to remember that person you've been meaning to call. For most people, that level of active coordination never quite happens, and the time slips by occupied by whatever was easiest.

There is a second layer to this problem. Leisure is deeply personal. Two people can both love the outdoors and have completely different criteria for what makes a day worth spending outside. One surfer wants long, slow, waist-high rollers and will paddle out in light rain. Another won't leave the house for anything under shoulder height with offshore wind. A cyclist might be happy riding in 10 degrees; another won't go below 16. No generic weather app or calendar tool can bridge that specificity. The result is that people either check too many things and still miss the moment, or they stop checking at all and outsource their free time to habit and inertia.

The problem, stated plainly: **people consistently miss the leisure moments that matter most to them because the right information never reaches them at the right time, and no tool exists that understands their personal criteria well enough to close that gap.**

This is not about productivity. It is not about optimizing or quantifying life. It is about the quiet loss of doing less of what you love than you could — not because the opportunity wasn't there, but because no one told you it was.

---

## The solution

Kairos is a personal leisure assistant that knows who you are, watches the world on your behalf, and speaks up at the right moment.

At its core, Kairos does three things: it learns your preferences in detail, it monitors the conditions and signals that matter for each of your activities, and it proactively reaches out — through Telegram, or wherever you prefer — when a genuine opportunity aligns with your calendar.

You tell Kairos what you love to do and what makes each activity worth doing for you specifically. For surfing, that means wave height, wind direction, swell period, your skill level, and which spots you're willing to drive to. For cycling, it might be temperature range, maximum rain probability, and whether you prefer a weekday morning or a weekend. For calling friends, it might be a list of people you want to stay in touch with and how often. You configure these once, in as much or as little detail as you like, and Kairos holds them.

From that point on, Kairos runs quietly in the background. Twice a day, it checks the forecast for the next 48 hours against your thresholds. It reads your Google Calendar to find where you have real free time. It cross-references those two things with your profile and scores each possible window for each of your hobbies. When it finds a genuine match — not just acceptable conditions, but conditions that actually meet your personal bar, in a slot you actually have free — it sends you a short, specific message. Not a push notification from a weather app that requires you to do the reasoning yourself. A message that says: tomorrow morning, 8 to 11, the swell is 1.4 metres with light offshore wind, you have nothing in your calendar, and it's 40 minutes from your place. This is the kind of morning you've been waiting for.

You can confirm with one tap, and Kairos adds it to your calendar. You can dismiss it, snooze it, or tell it the suggestion was off — and it learns.

The design principle behind Kairos is that the assistant should do the work you would do if you had time and perfect information. It should not overwhelm you. On a week when the weather is poor and your calendar is packed, it stays quiet. On a week when a rare opportunity opens up, it makes sure you don't miss it.

Over time, Kairos expands across the full texture of leisure. It notices when a film you would love is showing nearby on a rainy evening when you happen to be free. It notices that you haven't called your brother in six weeks and your Sunday afternoon is open. It notices that the mountain trail you wanted to hike is best in October and that there's a three-day gap in your calendar in mid-October that you haven't filled. It notices these things before you do, and it asks, gently: do you want to use this moment?

Kairos is not a scheduler. It does not tell you how to live or fill every gap in your calendar. It does one thing: it makes sure that the moments that matter to you don't quietly disappear without you noticing they were there.

---

## Continuous learning and the living profile

Kairos is not a form you fill in once. It is a system that builds its understanding of you over time — through conversation, through your responses to suggestions, and through the natural flow of what you tell it about your life. The user profile is not a static configuration; it is a living document that grows more accurate the longer you use the app.

### How Kairos first gets to know you

Onboarding begins with a conversation, not a settings screen. When a new user connects — via Telegram, or in future via WhatsApp — Kairos opens a dialogue: it asks about their life, their hobbies, what they love to do when they actually have time, what they've been meaning to do more of, and what's been getting in the way. This is intentionally open-ended. The user doesn't need to know what parameters to configure or which categories exist. They just talk, and Kairos listens.

From that conversation, Kairos extracts structured knowledge — activities, thresholds, locations, contacts, preferences — and writes it into the user's profile. The user can confirm, correct, or expand on it. If the onboarding conversation happens over WhatsApp messages forwarded into the system, or across several short exchanges over a few days, that is fine. The profile builds incrementally. There is no requirement to complete everything upfront.

### Ongoing learning from every interaction

Every interaction with Kairos is a potential update to the profile. When a user dismisses a suggestion, that is information — maybe the conditions weren't quite right, maybe the timing was off, maybe they've gone off that activity for a while. When they confirm one, that is information too. When they reply to a message in natural language — "actually I'm not really doing yoga anymore" or "I've been getting into padel lately" — Kairos reads that, extracts the relevant update, and revises the profile accordingly.

This is not pattern recognition from aggregate data. It is explicit, transparent knowledge management. Every piece of persistent information Kairos holds about a user should be something the user could read, verify, and correct. The profile is always inspectable: at any point, the user can ask Kairos "what do you know about me?" and receive a clear, readable summary of everything it is using to make decisions.

### Regular check-ins

Kairos runs a lightweight check-in with each user every one to two weeks, calibrated to their preferences. This is not a survey or a form. It is a short conversational message — something like: "Anything coming up in the next few weeks I should know about?" or "How have the suggestions been landing lately — anything you'd like more or less of?"

These check-ins serve multiple purposes. They surface upcoming events that aren't in the calendar yet: a trip abroad, a period of heavy work, a family visit, a wedding. They catch life changes before they cause bad suggestions. And they give the user a natural moment to update Kairos on anything that has shifted — a new hobby, a new location, a change in routine. The check-in is short and optional. If the user ignores it, nothing breaks. If they respond with two sentences, Kairos processes them and updates the profile accordingly.

### Handling life changes and temporary states

Life is not stable, and Kairos needs to reflect that. If a user mentions they've broken their arm, Kairos should immediately suppress all physical activity suggestions for an appropriate recovery period and check back in at a reasonable interval — "how's the arm doing, are you getting back to things?" If they mention they're traveling for three weeks, Kairos should adjust its location assumptions for that window and avoid suggesting activities that require being home. If they mention they've started a new job with longer hours, Kairos should recalibrate how frequently it suggests things and what kind of time windows it's looking for.

These are not edge cases. They are the normal texture of a person's life, and an assistant that doesn't account for them quickly becomes irrelevant or annoying. The goal is for Kairos to always feel like it knows what's going on — because it asked, and it remembered.

Temporary states have expiry logic built in. A broken arm doesn't suppress cycling suggestions forever; it suppresses them for six to eight weeks and then gently checks whether the user is ready to return. A holiday suppression lifts when the travel window ends. A "I'm in a really busy period at work" flag reduces suggestion frequency for a few weeks and then resets unless the user indicates otherwise. Kairos holds these states explicitly, not inferentially, so the user can always see what's affecting their experience and override it if needed.

### What gets stored, and what gets forgotten

Not everything the user mentions should be retained permanently. Kairos distinguishes between persistent knowledge (interests, thresholds, contacts, long-term preferences, location) and transient context (current mood, this week's plan, a one-off comment). Persistent knowledge is written to the user profile and stays until updated or deleted. Transient context informs the current interaction but does not accumulate.

Users can also explicitly instruct Kairos to forget specific things. If they no longer want a certain contact tracked, or they've given up a hobby, or they moved to a new city, they can say so conversationally and the profile updates immediately. There is no hidden data. There is no stale configuration quietly steering suggestions in the wrong direction.

The design principle is simple: Kairos should feel like it knows you well, because it has been paying attention. Not because it is running sophisticated inference on your behaviour, but because it asked, you told it, and it remembered correctly.

---

## User stories

### 1. Mo, 28, surfer and cyclist, relocating to Lisbon

Mo has been surfing for six years. He's comfortable in head-high waves and has specific requirements: he wants offshore or cross-shore wind below 15 knots, wave height between 1.0 and 2.5 metres, and he strongly prefers early mornings. He also cycles regularly and aims to ride at least twice a week when the weather is right. He works in tech, keeps a busy schedule, and often means to check the surf report the night before but forgets until he's already at his desk.

Since setting up Kairos, Mo gets a message roughly three mornings a week. Most of them he dismisses — the window is real but he has an early call, or he's tired, or the conditions are just barely above his threshold. But once or twice a week, the message is exactly right: tomorrow, 7:30 to 10:30, 1.6 metres, westerly swell, light offshore wind. He taps confirm, the session goes into his calendar, and he's in the water by 8. On the days when he'd have otherwise slept in and worked through a perfect morning, Kairos caught it for him.

He's also set up his cycling profile: minimum 14°C, rain probability under 20%, and a preference for routes in Sintra on weekends. When those conditions line up with a Saturday or Sunday morning, he gets a short nudge. He's done more weekend rides in the last two months than in the previous six.

---

### 2. Anneka, 41, mother of two, occasional hiker and committed reader

Anneka grew up hiking in the Black Forest and has lived in Munich for fifteen years. She hikes four or five times a year when she's organized enough to plan it, but her family schedule is dense and the planning always falls away. She's also a voracious reader who keeps a list of forty books she intends to read and usually reads about six a year, mostly on holiday.

She configured Kairos with her two main activities: hiking (minimum half-day free, temperature above 8°C, no rain, within 60 minutes of Munich), and reading (any rainy or cold evening with at least 90 minutes free, or a commute window over 40 minutes). She also added three friends she wants to call monthly and her mother, who she wants to speak to every two weeks.

Kairos doesn't overwhelm her. On a typical week she gets one or two messages. When a clear autumn Saturday opens up and the forecast for the Bavarian foothills is exceptional, she gets a note on Thursday evening: Saturday looks ideal for a hike — you're free from 9am, clear skies, 14 degrees, a trail near Garmisch takes about three hours. She confirms, adds it to the family calendar, and actually goes.

On a wet Tuesday evening with nothing in her diary, she gets a different kind of message: you have a free evening, it's raining, and you've been meaning to read *The Lonely City* for eight months. She usually smiles and puts her phone down, but she's knocked three books off her list in three months — more than she managed the previous year.

---

### 3. Darian, 34, tennis player and social connector

Darian plays tennis three to four times a week when possible and is the kind of person who considers himself good at staying in touch with people but is slowly realising he's not. He has a group of six close friends scattered across London and Hamburg; in practice, he sees most of them twice a year and calls more sporadically than he'd admit. He's also been meaning to get back into indoor climbing for a year.

He set up Kairos with his tennis preferences (outdoor courts only, above 12°C, no rain, mornings or lunch slots preferred), his contacts list with desired call frequencies ranging from "monthly" to "every six weeks," and climbing as a low-priority reminder ("remind me monthly if I haven't gone").

On clear mornings when he has a free slot before work, Kairos sends him a short note suggesting he book a court. He's started using those windows deliberately, and his tennis has improved. More unexpectedly, the friends feature has changed his social life more than he expected. He gets a message once a week or so: you haven't spoken to Felix in seven weeks — here's a suggested time this Sunday afternoon when you're free. He taps to confirm, sets a reminder, and makes the call. Felix mentioned twice that Darian seemed to be "going through a friendly phase." He didn't explain.

The climbing prompt has fired three times. He's gone once, which he considers a success.

---

## Activities Kairos can support

The following is a representative list of activities across all major leisure categories that Kairos can track, evaluate, and suggest. Each activity can be configured with personal thresholds, frequency preferences, location constraints, and calendar requirements.

---

### Outdoor and nature sports

- Surfing — wave height, swell period, wind direction and speed, tide, spot distance, skill level
- Kitesurfing — wind speed range, wave size, spot, season preferences
- Windsurfing — similar to kitesurfing, with rig configuration awareness
- Wingfoiling — lighter wind threshold than kite, flat water preference
- Road cycling — temperature, rain probability, wind, route type, distance target
- Mountain biking — trail conditions, precipitation in last 48h, temperature, terrain preference
- Hiking — duration, elevation, trail distance, temperature, precipitation, daylight hours
- Trail running — similar to hiking, shorter duration windows accepted
- Open water swimming — water temperature (via marine API), air temperature, wave height
- Wild swimming — river or lake locations, seasonal availability, minimum temperature
- Stand-up paddleboarding — wind speed, wave height, suitable body of water proximity
- Kayaking or canoeing — river level, wind, access point proximity
- Rock climbing (outdoor) — no rain for 24h prior, temperature, cliff dryness window
- Via ferrata — weather window, route difficulty match, group size preference
- Sailing — wind range, sea state, departure port
- Skiing or snowboarding — snow depth, piste conditions, travel time to resort, powder alerts
- Cross-country skiing — snow cover, groomed trail status, temperature
- Snowshoeing — snow depth, temperature, avalanche risk level
- Fishing — species-specific conditions, tidal windows, moon phase, river level
- Bird watching — migration season, location, dawn window, quiet conditions
- Beach days — UV index, temperature, wind, tide, beach crowding (weekday vs weekend)
- Wild foraging — seasonal (mushroom season, berry season), recent rainfall, woodland proximity

---

### Fitness and training

- Running — temperature, humidity, rain, air quality index, preferred time of day
- Gym sessions — calendar gap, minimum duration, proximity to home or work
- Indoor climbing — minimum duration, gym opening hours, training goal (bouldering vs lead)
- Swimming (pool) — lane availability, session length, training phase
- Yoga — home sessions on calm mornings, or studio classes based on schedule
- Strength training — rest day tracking, progressive overload reminders, session gap alerts
- HIIT or group fitness — class schedule alignment with free calendar windows
- Tennis — outdoor weather thresholds, court availability, partner coordination
- Padel — weather, partner availability, court booking windows
- Squash — indoor, weather-independent; purely calendar-driven
- Golf — temperature, wind, rain, tee time availability, daylight
- Badminton or table tennis — indoor, schedule-based
- Martial arts or boxing — class schedule, recovery time since last session
- Stretching or mobility — any short free window, morning preference
- Cycling on a trainer — rainy-day alternative suggestion when outdoor cycling is blocked

---

### Social and connection

- Calls with close friends — recency tracking, user-set frequency, free window matching
- Calls with family members — same, with priority weighting per contact
- Video calls with distant friends or family — time zone awareness, evening windows
- Meeting a local friend for coffee or lunch — weather, calendar, last-seen date, proximity
- Hosting a dinner — weekend evening, preparation lead time, guest availability hint
- Game nights or gatherings — weekend scheduling, recurring group coordination
- Writing a letter or long-form message to someone — quiet evening, no screen fatigue
- Attending a local community event — sourced from local event APIs, preference-matched

---

### Culture and entertainment

- Cinema — genre preferences, new releases, rainy day window, local showings, ticket availability
- Theatre or opera — advance booking alerts, seasonal programming, preference match
- Concerts or live music — artist watchlist alerts, venue proximity, weeknight vs weekend preference
- Museum or gallery visits — temporary exhibitions, quiet times (weekday mornings), free entry windows
- Comedy nights or spoken word — city listings, mood-based suggestion
- Sports matches (watching) — team or sport follow, fixture calendar, home or away
- Film nights at home — streaming new releases, genre queue, rainy or cold evening windows

---

### Learning and growth

- Language learning — daily streak protection, optimal session length, Duolingo or Anki integration
- Reading — book queue, session length, quiet evening or commute window
- Listening to podcasts or audiobooks — commute detection, workout pairing, long drive windows
- Online courses — chapter-length alignment with available time, course progress tracking
- Instrument practice — minimum session length (e.g. 30 minutes), daily or weekly cadence
- Drawing or painting — quiet afternoon window, daylight for natural light preference
- Writing (journaling, fiction, essays) — morning preference, uninterrupted block, streak tracking
- Photography — golden hour alerts, interesting weather, interesting locations nearby
- Cooking a new recipe — weekend afternoon, recipe complexity matched to time available
- Attending a workshop or class — local listings, skill interest match, advance booking alert

---

### Rest, mindfulness, and wellbeing

- Meditation — morning window, minimum 10–20 minutes, streak support
- Breathwork or cold exposure — morning, specific routine reminders
- Napping — circadian timing suggestion (post-lunch), duration guidance
- Digital detox windows — no-screen evening suggestions on low-commitment days
- Sauna or spa — local facilities, recovery-day scheduling, seasonal preference
- Massage or physiotherapy — recovery tracking, booking reminder, overdue alert
- Nature walks (non-sport) — stress-reduction framing, any weather threshold, park proximity
- Sunrise or sunset watching — golden hour alert, clear sky condition, viewpoint suggestion

---

### Planning and life admin (leisure-adjacent)

- Booking a weekend trip — far-enough-ahead calendar gap, seasonal destination matching, price alert
- Planning a holiday — long calendar window detection (5+ days free), destination wish list, advance booking nudge
- Buying event tickets before they sell out — artist or event watchlist, on-sale alerts, calendar pre-check
- Visiting family — travel window detection, long weekends, frequency since last visit
- Trying a new restaurant — special occasion proximity, cuisine preference, neighbourhood exploration
- Making a reservation for something worth booking ahead — seasonal restaurants, popular experiences, birthday proximity

---

*Activities are grouped by category for clarity. In practice, each is simply a module within Kairos with its own data sources, scoring logic, and suggestion cadence. The system is designed so that any activity with a timing dimension — conditions, calendar, recency, or season — can be plugged in without changing the core loop.*
