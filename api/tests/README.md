# API Tests

This directory contains all tests for the API app, organized by component type.

## Structure

```
tests/
├── __init__.py              # Makes this a Python package
├── test_settings.py         # Test-specific settings and base classes
├── test_models.py           # Tests for Planet model
├── test_serializers.py      # Tests for DRF serializers
├── test_views.py            # Tests for API views and endpoints
├── test_services.py         # Tests for business logic services
├── test_urls.py             # Tests for URL routing
├── test_management.py       # Tests for Django management commands
└── test_integration.py      # End-to-end integration tests
```

## Test Categories

### Unit Tests
- **test_models.py**: Tests for the Planet model, including field validation, methods, and database operations
- **test_serializers.py**: Tests for DRF serializers, including validation, serialization, and deserialization
- **test_services.py**: Tests for business logic services (GraphQL client, data generator, sync service)

### Integration Tests
- **test_views.py**: Tests for API endpoints and ViewSet behavior
- **test_urls.py**: Tests for URL routing and reverse lookups
- **test_management.py**: Tests for Django management commands

### End-to-End Tests
- **test_integration.py**: Tests that verify the complete flow from API request to database

## Running Tests

### Run all tests:
```bash
python manage.py test api.tests
```

### Run specific test categories:
```bash
# Models only
python manage.py test api.tests.test_models

# Views only
python manage.py test api.tests.test_views

# Services only
python manage.py test api.tests.test_services
```

### Run with coverage:
```bash
coverage run --source='.' manage.py test api.tests
coverage report
```

## Best Practices

1. **Test Isolation**: Each test should be independent and not rely on other tests
2. **Mocking**: Use mocks for external dependencies (APIs, databases)
3. **Fixtures**: Use shared fixtures in `conftest.py` for common test data
4. **Naming**: Test methods should clearly describe what they're testing
5. **Assertions**: Use specific assertions that test one thing at a time

## Common Patterns

### Testing API Endpoints
```python
def test_planet_list(self):
    response = self.client.get('/api/planets/')
    self.assertEqual(response.status_code, 200)
```

### Testing with Mocks
```python
@patch('api.services.graphql_client.logger')
def test_graphql_error(self, mock_logger):
    # Test implementation
    pass
```

### Testing Model Methods
```python
def test_planet_string_representation(self):
    planet = self.create_sample_planet()
    self.assertEqual(str(planet), "Test Planet")
```
