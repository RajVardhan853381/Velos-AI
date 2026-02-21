.PHONY: dev test lint format build migrate setup

# Development
dev:
	docker-compose up -d
	@echo "Services started natively. Backend at :8000, Frontend at :5173"

dev-logs:
	docker-compose logs -f

stop:
	docker-compose down

# Database
migrate:
	docker-compose exec backend alembic upgrade head

makemigrations:
	docker-compose exec backend alembic revision --autogenerate -m "auto"

# Utility
setup:
	cp .env.example .env
	@echo "Please fill in .env before running 'make dev'"

# Testing & Linting
test:
	docker-compose exec backend pytest backend/tests/ -v

lint:
	docker-compose exec backend ruff check backend/
	cd velos-frontend && npm run lint

format:
	docker-compose exec backend ruff format backend/
	cd velos-frontend && npm run format

demo-setup:
	PYTHONPATH="$(PWD)" JWT_SECRET="mock_jwt_secret_for_demo" ETHEREUM_PRIVATE_KEY="0xdeadbeef" python3 scripts/seed_demo_data.py
	@echo "Demo Instance Ready at http://localhost:5173"
