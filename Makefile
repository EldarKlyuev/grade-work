.PHONY: help up down logs migrate seed test clean install dev lint build

help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies with Poetry"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - View application logs"
	@echo "  make migrate  - Run database migrations"
	@echo "  make seed     - Seed database with sample data"
	@echo "  make test     - Run tests"
	@echo "  make lint     - Run linters"
	@echo "  make build    - Build production Docker image"
	@echo "  make clean    - Remove containers and volumes"

install:
	poetry install

up:
	docker-compose up -d
	@echo "Services started. API: http://localhost:8000/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f app

migrate:
	docker-compose exec app alembic upgrade head

seed:
	docker-compose exec app python scripts/seed_data.py

test:
	docker-compose exec app poetry run pytest

lint:
	poetry run ruff check src tests
	poetry run mypy src

build:
	docker build -t grade-work:latest .

clean:
	docker-compose down -v
	rm -rf .venv __pycache__ **/__pycache__ .pytest_cache

dev:
	poetry run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
