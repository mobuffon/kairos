#!/usr/bin/env bash
# Telegram webhook helpers — sourced env from .env, masks tokens in output.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  echo "ERROR: .env not found. Copy .env.example to .env first." >&2
  exit 1
fi

set -a
# shellcheck disable=SC1091
source ./.env
set +a

mask_token() {
  python3 -c "t='${1:-}'; print(t[:8]+'...' if len(t)>8 else '(empty)')"
}

require_bot_token() {
  if [[ -z "${TELEGRAM_BOT_TOKEN:-}" || "${TELEGRAM_BOT_TOKEN}" == "..." ]]; then
    echo "ERROR: Set TELEGRAM_BOT_TOKEN in .env (from @BotFather /newbot)." >&2
    exit 1
  fi
}

require_webhook_secret() {
  if [[ -z "${TELEGRAM_WEBHOOK_SECRET:-}" || "${TELEGRAM_WEBHOOK_SECRET}" == "change-me-to-random-32-char-string" ]]; then
    echo "ERROR: Generate TELEGRAM_WEBHOOK_SECRET: openssl rand -hex 32" >&2
    exit 1
  fi
}

ngrok_https_url() {
  curl -sf http://localhost:4040/api/tunnels | python3 -c "
import json, sys
data = json.load(sys.stdin)
for t in data.get('tunnels', []):
    url = t.get('public_url', '')
    if url.startswith('https'):
        print(url)
        break
else:
    sys.exit(1)
"
}

cmd_set() {
  require_bot_token
  require_webhook_secret
  NGROK_URL="$(ngrok_https_url)" || {
    echo "ERROR: ngrok not reachable on localhost:4040. Run: make ngrok" >&2
    exit 1
  }
  WEBHOOK_URL="${NGROK_URL}/bot/webhook"
  echo "Bot token: $(mask_token "$TELEGRAM_BOT_TOKEN")"
  echo "Setting webhook to $WEBHOOK_URL"
  echo "(secret_token from TELEGRAM_WEBHOOK_SECRET — not printed)"
  curl -sf -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
    -d "url=${WEBHOOK_URL}" \
    -d "secret_token=${TELEGRAM_WEBHOOK_SECRET}"
  echo
  cmd_info
}

cmd_info() {
  require_bot_token
  echo "Webhook info for bot token $(mask_token "$TELEGRAM_BOT_TOKEN"):"
  curl -sf "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo" | python3 -m json.tool
}

cmd_test() {
  require_webhook_secret
  SECRET="${TELEGRAM_WEBHOOK_SECRET}"
  echo "POST http://localhost:8000/bot/webhook (secret header set, value not printed)"
  curl -sf -X POST "http://localhost:8000/bot/webhook" \
    -H "Content-Type: application/json" \
    -H "X-Telegram-Bot-Api-Secret-Token: ${SECRET}" \
    -d '{"update_id":99999,"message":{"message_id":1,"date":0,"text":"/start","chat":{"id":123456789,"type":"private"}}}' \
    | python3 -m json.tool
}

cmd_health_ngrok() {
  NGROK_URL="$(ngrok_https_url)" || {
    echo "ERROR: ngrok not reachable on localhost:4040. Run: make ngrok" >&2
    exit 1
  }
  echo "GET ${NGROK_URL}/health"
  curl -sf "${NGROK_URL}/health" | python3 -m json.tool
}

case "${1:-}" in
  set) cmd_set ;;
  info) cmd_info ;;
  test) cmd_test ;;
  health) cmd_health_ngrok ;;
  *)
    echo "Usage: $0 {set|info|test|health}" >&2
    exit 1
    ;;
esac
