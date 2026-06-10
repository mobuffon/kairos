# Telegram bot setup (local dev)

Follow this guide from zero when Telegram integration is not working or you want a **fresh bot**. Each step builds on the previous one.

## What you need

- Telegram app on your phone
- This repo running with Docker
- An [ngrok authtoken](https://dashboard.ngrok.com/get-started/your-authtoken) (free tier is fine)

---

## Step 1 — Create a new bot on your phone

Do this on your phone in the Telegram app:

1. Open Telegram and search for **@BotFather** (verified account with checkmark).
2. Tap **Start** (or send `/start`).
3. Send **`/newbot`**.
4. BotFather asks for a **display name** — anything you like, e.g. `Kairos Dev`.
5. BotFather asks for a **username** — must end in `bot`, e.g. `kairos_dev_mo_bot`.
6. BotFather replies with a message containing your **HTTP API token** (long string like `7123456789:AAH...`).

**Copy the token now** — you will paste it into `.env` in Step 2. BotFather will not show it again in full (only `/token` to regenerate).

Optional: send `/setdescription` and `/setabouttext` to BotFather if you want a nicer bot profile.

---

## Step 2 — Update `.env`

From the project root:

```bash
cp .env.example .env   # skip if .env already exists
```

Edit `.env` and set these values:

| Variable | Value |
|----------|-------|
| `TELEGRAM_BOT_TOKEN` | Paste the token from BotFather (Step 1) |
| `TELEGRAM_WEBHOOK_SECRET` | Generate: `openssl rand -hex 32` |
| `MOCK_EXTERNAL_APIS` | `false` |
| `NGROK_AUTHTOKEN` | Your ngrok authtoken |

Generate the webhook secret:

```bash
openssl rand -hex 32
```

Paste the output as `TELEGRAM_WEBHOOK_SECRET`.

**Important:** `TELEGRAM_WEBHOOK_URL` in `.env.example` is **documentation only**. The app does not read it. `make webhook-set` discovers the live ngrok URL automatically. Do not hand-edit `TELEGRAM_WEBHOOK_URL` and expect the webhook to update — always run `make webhook-set` after ngrok restarts.

Restart the app so it picks up the new env:

```bash
docker compose --profile ngrok up -d --build
```

---

## Step 3 — Start the stack with ngrok

```bash
docker compose --profile ngrok up -d
```

Or:

```bash
make ngrok
```

Confirm ngrok is up:

```bash
curl -s http://localhost:4040/api/tunnels | python3 -m json.tool
```

You should see an `https://….ngrok-free.dev` (or `.app`) public URL.

Check health through the tunnel:

```bash
make webhook-health
```

Expected:

```json
{
  "status": "ok",
  "db": "ok",
  "redis": "ok"
}
```

---

## Step 4 — Register the webhook (with secret)

```bash
make webhook-set
```

This calls Telegram `setWebhook` with:

- **url** — current ngrok HTTPS URL + `/bot/webhook`
- **secret_token** — your `TELEGRAM_WEBHOOK_SECRET` from `.env`

Output shows a masked bot token and prints `getWebhookInfo`. Verify:

- `"url"` ends with `/bot/webhook` and matches your current ngrok URL
- `"last_error_message"` is empty (or was cleared after a successful set)

Check anytime:

```bash
make webhook-info
```

---

## Step 5 — Test locally (before Telegram)

Simulate Telegram posting an update to your app:

```bash
make webhook-test
```

Expected response:

```json
{
  "ok": true,
  "update_id": 99999,
  "handled": true,
  "reply_sent": true,
  "mock": false
}
```

If you get **403 Invalid webhook secret**, your `TELEGRAM_WEBHOOK_SECRET` in `.env` does not match what Telegram sends (or `MOCK_EXTERNAL_APIS` is still `true` while testing with secret enforcement). Fix `.env` and restart the app container.

Watch logs:

```bash
make logs
```

You should see lines like:

```
webhook_received  update_id=99999  chat_id=123456789  text_preview=/start
webhook_handled   handled=True  reply_sent=True
```

---

## Step 6 — Test from Telegram

1. In Telegram, search for your bot by **username** (e.g. `@kairos_dev_mo_bot`).
2. Tap **Start** or send **`/start`**.

**Expected bot reply:**

> Welcome to Kairos! I watch the weather, your calendar, and your hobbies to suggest the right moment for things you love.
>
> Tell me about your location and hobbies, or use the web app to set up.

**Expected app logs** (`make logs`):

```
webhook_received  update_id=<n>  chat_id=<your_chat_id>  text_preview=/start  mock=false
webhook_handled   handled=True  reply_sent=True  mock=false
```

If `mock=true` appears, the app is still in mock mode — check `MOCK_EXTERNAL_APIS=false` and a real `TELEGRAM_BOT_TOKEN`, then restart containers.

---

## How it works (code path)

```
Telegram → ngrok → POST /bot/webhook
         → backend/api/bot.py (validates X-Telegram-Bot-Api-Secret-Token)
         → bot/telegram/webhook.py handle_webhook_update()
         → /start → send_message() welcome text
```

### Does `/start` send a message?

**Yes.** `handle_webhook_update` builds a welcome string and calls `send_message(chat_id, reply)`. With a real token and `MOCK_EXTERNAL_APIS=false`, that hits the Telegram Bot API.

### Is a user created in the database on `/start`?

**Not yet.** `/start` only sends the welcome message. User rows are not created automatically; onboarding still uses mock fixtures for non-`/start` messages. DB-backed user creation is planned for a later phase.

---

## Replacing an old bot (all three steps)

If you previously used a different bot token, stale webhooks and secrets cause silent failures. When switching bots:

1. **Create a new bot** with BotFather (`/newbot`) — do not reuse the old token.
2. **Replace in `.env`:**
   - `TELEGRAM_BOT_TOKEN` → new token
   - `TELEGRAM_WEBHOOK_SECRET` → new `openssl rand -hex 32` (recommended)
   - `MOCK_EXTERNAL_APIS=false`
3. **Restart and re-register:**
   ```bash
   docker compose --profile ngrok up -d --build
   make webhook-set
   ```
4. **Message the new bot** in Telegram (old chat threads may still point at the old bot).

You do not need to delete the old bot in BotFather, but you must not mix old token + new secret or old webhook URL.

---

## Troubleshooting

### 403 Invalid webhook secret

- `TELEGRAM_WEBHOOK_SECRET` in `.env` must match what was sent to `setWebhook` as `secret_token`.
- Re-run `make webhook-set` after changing the secret.
- Restart the app: `docker compose up -d app`
- Local test: `make webhook-test` (uses the same secret from `.env`).

### ngrok URL changed

Free ngrok URLs change when the ngrok container restarts. Symptom: Telegram `getWebhookInfo` shows old URL or delivery errors.

```bash
make webhook-set
make webhook-info
```

### No reply in Telegram but logs show `reply_sent: true`

- Confirm `mock=false` in logs.
- Check token is valid: `make webhook-info` should not show `"Unauthorized"`.
- Ensure you are messaging the **same bot** whose token is in `.env`.

### `make webhook-set` fails: ngrok not reachable

```bash
docker compose --profile ngrok up -d
curl http://localhost:4040/api/tunnels
```

Set `NGROK_AUTHTOKEN` in `.env` if ngrok exits immediately.

### `make webhook-set` fails: invalid token

Token is wrong or revoked. In BotFather: `/mybots` → your bot → **API Token** → regenerate, update `.env`, restart, `make webhook-set`.

### Health OK locally but Telegram never hits webhook

- Run `make webhook-info` — URL must be HTTPS and reachable.
- Visit ngrok URL in browser once if using ngrok free tier (interstitial can block API clients).
- Send `/start` again after fixing webhook.

### `MOCK_EXTERNAL_APIS=true`

Telegram outbound messages go to `data/mock_notifications.jsonl` instead of Telegram. Webhook secret checks are **skipped** in mock mode. For real Telegram, set `MOCK_EXTERNAL_APIS=false`.

---

## Make targets reference

| Command | Purpose |
|---------|---------|
| `make ngrok` | Start stack + ngrok tunnel |
| `make webhook-set` | Register webhook URL + secret with Telegram |
| `make webhook-info` | Show current webhook status (token masked) |
| `make webhook-test` | POST fake `/start` update to local app |
| `make webhook-health` | GET `/health` via ngrok public URL |
| `make logs` | Follow app logs |

---

## Production note

For a deployed domain, set webhook manually:

```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d "url=https://your-domain.com/bot/webhook" \
  -d "secret_token=<TELEGRAM_WEBHOOK_SECRET>"
```

Use the same `TELEGRAM_WEBHOOK_SECRET` in your production environment.
