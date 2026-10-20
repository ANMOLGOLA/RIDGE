.PHONY: help dev up down test seed demo lint

help:
	@echo "RIDGE Developer Commands:"
	@echo "  make dev      - Run backend and frontend locally"
	@echo "  make up       - Start all services with Docker Compose"
	@echo "  make down     - Stop Docker Compose services"
	@echo "  make seed     - Seed corridors, gazetteer, and train initial ML model"
	@echo "  make demo     - Run a scripted demo ingestion run"
	@echo "  make test     - Run backend and frontend tests"
	@echo "  make lint     - Run code quality linters"

up:
	docker compose up --build

down:
	docker compose down

seed:
	python -m backend.app.ml.train

demo:
	python -c "import httpx; res = httpx.post('http://localhost:8000/api/ingestion/run', json={'corridor': 'NH-10', 'mode': 'search'}); print('Ingestion triggered:', res.json())"

test:
	pytest backend/tests
