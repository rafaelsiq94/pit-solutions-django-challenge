# 🌌 Star Wars Planet API

[![Test Coverage](https://img.shields.io/badge/test%20coverage-96%25-brightgreen)](https://htmlcov.io/)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-5.2.5-green.svg)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/drf-3.16.1-red.svg)](https://www.django-rest-framework.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

A comprehensive Django REST API for managing Star Wars planets with automatic synchronization from GraphQL APIs, featuring a complete test suite.

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
- [API Endpoints](#-api-endpoints)
- [Installation](#-installation)
- [Testing](#-testing)
- [Docker Setup](#-docker-setup)
- [Development](#-development)

## ✨ Features

### 🌟 Core Features
- **RESTful API** - Complete CRUD operations for planets
- **GraphQL Integration** - Automatic synchronization from Star Wars GraphQL API
- **Data Generation** - Smart fake data generation for missing fields
- **Management Commands** - CLI tools for data synchronization
- **Comprehensive Testing** - Amazing code coverage

### 🔧 Technical Features
- **Django 5.2.5** - Latest Django framework
- **Django REST Framework** - Powerful API development
- **PostgreSQL Support** - Production-ready database
- **Docker Integration** - Containerized development and deployment
- **Health Checks** - Application and database monitoring
- **Automatic Migrations** - Database setup and updates

### 📊 Data Management
- **Planet Information** - Name, population, climates, terrains
- **External ID Tracking** - Unique identifiers for API synchronization
- **Timestamps** - Created and updated tracking
- **Data Validation** - Comprehensive input validation
- **Error Handling** - Robust error management

## 🚀 Quick Start

### Using Docker (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd pit-solutions-django-challenge

# Start the application
make docker-dev

# Access the API
curl http://localhost:8000/api/planets/

# Sync planets from GraphQL API
make docker-sync
```

### Using Local Development
```bash
# Install dependencies
make install

# Run migrations
make migrate

# Start development server
make run

# Run tests
make test
```

## 🔌 API Endpoints

### Planets API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/planets/` | List all planets |
| `POST` | `/api/planets/` | Create a new planet |
| `GET` | `/api/planets/{id}/` | Get planet details |
| `PUT` | `/api/planets/{id}/` | Update planet |
| `DELETE` | `/api/planets/{id}/` | Delete planet |

### Sync Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/planets/sync/` | Sync all planets from GraphQL API |
| `GET` | `/api/planets/sync-status/` | Get synchronization status |

### Example API Usage

```bash
# Get all planets
curl http://localhost:8000/api/planets/

# Create a planet
curl -X POST http://localhost:8000/api/planets/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tatooine",
    "population": 200000,
    "climates": ["arid"],
    "terrains": ["desert"]
  }'

# Sync planets from GraphQL API
curl -X POST http://localhost:8000/api/planets/sync/

# Check sync status
curl http://localhost:8000/api/planets/sync-status/
```

## 📦 Installation

### Prerequisites
- Python 3.11+
- Docker (optional, for containerized setup)

### Local Setup
```bash
# Clone repository
git clone <repository-url>
cd pit-solutions-django-challenge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install

# Run migrations
make migrate

# Create superuser
make superuser

# Start development server
make run
```

### Environment Variables
```bash
# Development (SQLite)
DEBUG=True
DJANGO_SETTINGS_MODULE=challenge.settings

# Production (PostgreSQL)
DEBUG=False
SECRET_KEY=your-secret-key
POSTGRES_DB=django_db
POSTGRES_USER=django_user
POSTGRES_PASSWORD=django_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

## 🧪 Testing

### Run All Tests
```bash
# Run all 100 tests
make test

# Run with coverage report
make test-coverage

# Generate coverage badge for README
make coverage-badge
```

### Test Categories
```bash
# Run specific test categories
make test-models      # Model tests
make test-views       # View tests
make test-services    # Service tests
make test-serializers # Serializer tests
make test-urls        # URL tests
make test-management  # Management command tests
make test-integration # Integration tests
```

### Test Coverage
- **Tests** covering all components
- **Code coverage** with detailed reports
- **HTML coverage report** in `htmlcov/index.html`
- **Coverage treemap** for visual analysis

## 🐳 Docker Setup

### Quick Start with Docker
```bash
# Build and start containers
make docker-dev

# View logs
make docker-logs

# Run tests in Docker
make docker-test

# Sync planets in Docker
make docker-sync
```

### Docker Commands
```bash
# Container management
make docker-up        # Start containers
make docker-down      # Stop containers
make docker-logs      # View logs
make docker-shell     # Open shell in container

# Database operations
make docker-migrate   # Run migrations
make docker-superuser # Create superuser
make docker-db-reset  # Reset database

# Testing in Docker
make docker-test      # Run tests
make docker-test-coverage  # Run tests with coverage
```

### Docker Services
- **Web Service** - Django application (port 8000)
- **Database Service** - PostgreSQL (port 5432)
- **Health Checks** - Automatic monitoring
- **Volume Persistence** - Data persistence

## 🛠️ Development

### Available Make Commands
```bash
# Development workflow
make dev              # Install, migrate, run
make setup            # Complete setup
make clean            # Clean cache files
make check            # Django system check

# Database operations
make migrate          # Apply migrations
make makemigrations   # Create migrations
make db-reset         # Reset database

# API operations
make sync             # Sync planets
make sync-status      # Check sync status
make status           # Application status
```

### Development Workflow
1. **Start Environment**
   ```bash
   make docker-dev
   ```

2. **Make Changes** (files are mounted as volumes)

3. **Run Tests**
   ```bash
   make docker-test
   ```

4. **Apply Migrations**
   ```bash
   make docker-migrate
   ```

5. **Restart if Needed**
   ```bash
   make docker-down && make docker-up
   ```
