"""
Test-specific settings for the API app.
"""

from django.test import TestCase


class APITestCase(TestCase):
    """Base test case for API tests with common setup."""

    def setUp(self):
        """Set up common test data."""
        super().setUp()
        self.sample_planet_data = {
            "external_id": "test-123",
            "name": "Test Planet",
            "population": 1000000,
            "climates": ["temperate", "tropical"],
            "terrains": ["forest", "mountains"],
        }

    def create_sample_planet(self, **kwargs):
        """Create a sample planet for testing."""
        from api.models import Planet

        data = self.sample_planet_data.copy()
        data.update(kwargs)
        return Planet.objects.create(**data)
