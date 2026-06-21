.PHONY: help db db-down install seed dev test selftest reset

BACKEND = backend
DB_CONTAINER = spothound-db-1

help:  ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

db:  ## Start local Postgres and wait until it's ready
	docker compose up -d db
	@until docker exec $(DB_CONTAINER) pg_isready -U spothound >/dev/null 2>&1; do sleep 1; done
	@echo "postgres ready"

db-down:  ## Stop Postgres and delete its data
	docker compose down -v

install:  ## Install backend dependencies (uv)
	cd $(BACKEND) && uv sync

seed:  ## Create admin user + sync spots into targets
	cd $(BACKEND) && uv run python -m app.seed

dev:  ## Run the API + scheduler with autoreload
	cd $(BACKEND) && uv run uvicorn app.main:app --reload

test:  ## Run every spot through the engine (no DB needed)
	cd $(BACKEND) && uv run python selftest.py

selftest:  ## Run one spot: make selftest spot=<spot_key>
	cd $(BACKEND) && uv run python selftest.py $(spot)

reset: db-down db seed  ## Recreate the DB from scratch and reseed
