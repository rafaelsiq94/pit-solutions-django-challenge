# Django Planet API Makefile
# Usage: make <command>

.PHONY: help install test test-coverage run migrate makemigrations shell superuser clean docker-build docker-up docker-down docker-logs docker-shell sync sync-status

# Default target
help:
	@echo "Django Planet API - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install          Install Python dependencies"
	@echo "  run              Start Django development server"
	@echo "  migrate          Apply database migrations"
	@echo "  makemigrations   Create new migrations"
	@echo "  shell            Open Django shell"
	@echo "  superuser        Create Django superuser"
	@echo ""
	@echo "Testing:"
	@echo "  test             Run all tests"
	@echo "  test-coverage    Run tests with coverage report"
	@echo "  test-models      Run model tests only"
	@echo "  test-views       Run view tests only"
	@echo "  test-services    Run service tests only"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build     Build Docker images"
	@echo "  docker-up        Start Docker containers"
	@echo "  docker-down      Stop Docker containers"
	@echo "  docker-logs      Show Docker logs"
	@echo "  docker-shell     Open shell in web container"
	@echo "  docker-clean     Remove containers and images"
	@echo ""
	@echo "API Operations:"
	@echo "  sync             Sync planets from GraphQL API"
	@echo "  sync-status      Check sync status"
	@echo ""
	@echo "Utilities:"
	@echo "  clean            Clean Python cache files"
	@echo "  check            Run Django system check"

# Development Commands
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt

run:
	@echo "Starting Django development server..."
	python manage.py runserver

migrate:
	@echo "Applying database migrations..."
	python manage.py migrate

makemigrations:
	@echo "Creating new migrations..."
	python manage.py makemigrations

shell:
	@echo "Opening Django shell..."
	python manage.py shell

superuser:
	@echo "Creating Django superuser..."
	python manage.py createsuperuser

# Testing Commands
test:
	@echo "Running all tests..."
	python manage.py test api.tests

test-coverage:
	@echo "Running tests with coverage..."
	coverage run --source='.' manage.py test api.tests
	coverage report
	coverage html

test-models:
	@echo "Running model tests..."
	python manage.py test api.tests.test_models

test-views:
	@echo "Running view tests..."
	python manage.py test api.tests.test_views

test-services:
	@echo "Running service tests..."
	python manage.py test api.tests.test_services

test-serializers:
	@echo "Running serializer tests..."
	python manage.py test api.tests.test_serializers

test-urls:
	@echo "Running URL tests..."
	python manage.py test api.tests.test_urls

test-management:
	@echo "Running management command tests..."
	python manage.py test api.tests.test_management

test-integration:
	@echo "Running integration tests..."
	python manage.py test api.tests.test_integration

# Docker Commands
docker-build:
	@echo "Building Docker images..."
	docker compose build

docker-up:
	@echo "Starting Docker containers..."
	docker compose up -d

docker-down:
	@echo "Stopping Docker containers..."
	docker compose down

docker-logs:
	@echo "Showing Docker logs..."
	docker compose logs -f

docker-logs-web:
	@echo "Showing web container logs..."
	docker compose logs -f web

docker-logs-db:
	@echo "Showing database container logs..."
	docker compose logs -f db

docker-shell:
	@echo "Opening shell in web container..."
	docker compose exec web bash

docker-migrate:
	@echo "Running migrations in Docker..."
	docker compose exec web python manage.py migrate

docker-superuser:
	@echo "Creating superuser in Docker..."
	docker compose exec web python manage.py createsuperuser

docker-test:
	@echo "Running tests in Docker..."
	docker compose exec web python manage.py test api.tests

docker-test-coverage:
	@echo "Running tests with coverage in Docker..."
	docker compose exec web coverage run --source='.' manage.py test api.tests
	docker compose exec web coverage report

docker-clean:
	@echo "Cleaning Docker containers and images..."
	docker compose down -v --rmi all
	docker system prune -f

# API Operations
sync:
	@echo "Syncing planets from GraphQL API..."
	python manage.py sync_planets

sync-status:
	@echo "Checking sync status..."
	python manage.py sync_planets --status

docker-sync:
	@echo "Syncing planets from GraphQL API in Docker..."
	docker compose exec web python manage.py sync_planets

docker-sync-status:
	@echo "Checking sync status in Docker..."
	docker compose exec web python manage.py sync_planets --status

# Utility Commands
clean:
	@echo "Cleaning Python cache files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/

check:
	@echo "Running Django system check..."
	python manage.py check

# Database Commands
db-reset:
	@echo "Resetting database (WARNING: This will delete all data)..."
	rm -f db.sqlite3
	python manage.py migrate
	python manage.py createsuperuser

docker-db-reset:
	@echo "Resetting database in Docker (WARNING: This will delete all data)..."
	docker compose down -v
	docker compose up -d db
	sleep 5
	docker compose exec web python manage.py migrate
	docker compose exec web python manage.py createsuperuser

# Development Setup
setup: install migrate
	@echo "Development environment setup complete!"

docker-setup: docker-build docker-up
	@echo "Docker environment setup complete!"

# Quick Development Workflow
dev: install migrate run

docker-dev: docker-up
	@echo "Docker development environment ready!"
	@echo "API available at: http://localhost:8000/api/planets/"
	@echo "Admin available at: http://localhost:8000/admin/"

# Production-like Commands
prod-check:
	@echo "Running production checks..."
	python manage.py check --deploy
	python manage.py test api.tests

# Documentation
docs:
	@echo "Generating API documentation..."
	python manage.py shell -c "from django.core.management import execute_from_command_line; execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])"

# Monitoring
status:
	@echo "Checking application status..."
	@echo "Docker containers:"
	docker compose ps
	@echo ""
	@echo "Database migrations:"
	python manage.py showmigrations
	@echo ""
	@echo "Sync status:"
	python manage.py sync_planets --status

docker-status:
	@echo "Checking Docker application status..."
	@echo "Containers:"
	docker compose ps
	@echo ""
	@echo "Database migrations:"
	docker compose exec web python manage.py showmigrations
	@echo ""
	@echo "Sync status:"
	docker compose exec web python manage.py sync_planets --status
