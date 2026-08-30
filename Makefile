.PHONY: install dev lint format typecheck test check run docker-up docker-down

install:      ## Install deps (incl. dev) into a uv-managed venv
	uv sync --extra dev

dev:          ## Run with autoreload
	uv run uvicorn app.main:app --reload

lint:         ## Lint
	uv run ruff check .

format:       ## Auto-format
	uv run ruff format .

typecheck:    ## Static type check
	uv run mypy app

test:         ## Run tests
	uv run pytest -q

check: lint typecheck test  ## Run the full local gate (matches CI)

run:          ## Run production-style server
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

docker-up:    ## Build + run via Docker Compose
	docker compose up --build

docker-down:  ## Stop Docker Compose
	docker compose down
