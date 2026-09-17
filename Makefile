.PHONY: install dev lint format format-check typecheck test check run docker-up docker-down

install:      ## Install deps (incl. dev) into a uv-managed venv
	uv sync --extra dev

dev:          ## Run backend with autoreload
	uv run uvicorn app.main:app --reload

lint:         ## Lint
	uv run ruff check .

format:       ## Auto-format
	uv run ruff format .

format-check: ## Check formatting without modifying files
	uv run ruff format --check .

typecheck:    ## Static type check
	uv run mypy app

test:         ## Run tests
	uv run pytest -q

check: lint format-check typecheck test  ## Run the backend CI gate locally

run:          ## Run production-style backend server
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

docker-up:    ## Build + run PostgreSQL + API + frontend
	docker compose up --build

docker-down:  ## Stop Docker Compose
	docker compose down
