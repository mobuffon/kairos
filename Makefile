.PHONY: dev dev-bg ngrok webhook-set webhook-info webhook-test webhook-health test lint migrate shell logs reset-db

# ── Development ──────────────────────────────────────────────────────────────

dev:
	docker-compose up --build

dev-bg:
	docker-compose up --build -d

# Start stack with ngrok tunnel for Telegram webhook local dev (requires NGROK_AUTHTOKEN in .env)
ngrok:
	docker-compose --profile ngrok up --build -d

# Telegram webhook helpers (see docs/TELEGRAM_SETUP.md)
webhook-set:
	@bash scripts/telegram_webhook.sh set

webhook-info:
	@bash scripts/telegram_webhook.sh info

webhook-test:
	@bash scripts/telegram_webhook.sh test

webhook-health:
	@bash scripts/telegram_webhook.sh health

stop:
	docker-compose down

logs:
	docker-compose logs -f app worker

# ── Database ──────────────────────────────────────────────────────────────────

migrate:
	docker-compose exec app alembic upgrade head

migrate-create:
	@read -p "Migration name: " name; \
	docker-compose exec app alembic revision --autogenerate -m "$$name"

migrate-down:
	docker-compose exec app alembic downgrade -1

reset-db:
	docker-compose down -v
	docker-compose up -d postgres
	sleep 2
	docker-compose exec app alembic upgrade head

# ── Testing ───────────────────────────────────────────────────────────────────

test:
	docker-compose exec app pytest tests/ -v

test-unit:
	docker-compose exec app pytest tests/unit/ -v

test-integration:
	docker-compose exec app pytest tests/integration/ -v

test-cov:
	docker-compose exec app pytest tests/ --cov=backend --cov-report=term-missing

# ── Linting ───────────────────────────────────────────────────────────────────

lint:
	docker-compose exec app ruff check backend/
	docker-compose exec app ruff format --check backend/

lint-fix:
	docker-compose exec app ruff check --fix backend/
	docker-compose exec app ruff format backend/

# ── Utility ───────────────────────────────────────────────────────────────────

shell:
	docker-compose exec app bash

psql:
	docker-compose exec postgres psql -U kairos -d kairos

redis-cli:
	docker-compose exec redis redis-cli

# ── Git shortcuts for agent ───────────────────────────────────────────────────

status:
	git log --oneline -10
	git status

save:
	@read -p "Commit message: " msg; \
	git add -A && git commit -m "$$msg"
