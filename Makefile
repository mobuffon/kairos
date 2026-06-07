.PHONY: dev test lint migrate shell logs reset-db

# ── Development ──────────────────────────────────────────────────────────────

dev:
	docker-compose up --build

dev-bg:
	docker-compose up --build -d

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
