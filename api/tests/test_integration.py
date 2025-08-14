from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, Mock


class PlanetIntegrationTest(TestCase):
    """Integration tests for the complete planet API flow."""

    def setUp(self):
        """Set up test data and client."""
        self.client = APIClient()
        self.planet_data = {
            "external_id": "test-123",
            "name": "Test Planet",
            "population": 1000000,
            "climates": ["temperate", "tropical"],
            "terrains": ["forest", "mountains"],
        }

    def test_complete_planet_lifecycle(self):
        """Test the complete lifecycle of a planet: create, read, update, delete."""
        # 1. Create a planet
        create_url = reverse("api:planet-list")
        response = self.client.post(create_url, self.planet_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        planet_id = response.data["id"]

        # 2. Retrieve the planet
        retrieve_url = reverse("api:planet-detail", args=[planet_id])
        response = self.client.get(retrieve_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Planet")
        self.assertEqual(response.data["external_id"], "test-123")

        # 3. Update the planet
        update_data = {
            "name": "Updated Test Planet",
            "population": 2000000,
            "climates": ["arid", "hot"],
            "terrains": ["desert", "canyons"],
        }
        response = self.client.put(retrieve_url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Test Planet")
        self.assertEqual(response.data["population"], 2000000)

        # 4. Partially update the planet
        partial_update_data = {"name": "Partially Updated Planet"}
        response = self.client.patch(retrieve_url, partial_update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Partially Updated Planet")
        # Other fields should remain unchanged
        self.assertEqual(response.data["population"], 2000000)

        # 5. List all planets
        list_url = reverse("api:planet-list")
        response = self.client.get(list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Partially Updated Planet")

        # 6. Delete the planet
        response = self.client.delete(retrieve_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # 7. Verify planet is deleted
        response = self.client.get(retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_multiple_planets_operations(self):
        """Test operations with multiple planets."""
        # Create multiple planets
        planets_data = [
            {
                "external_id": "planet-1",
                "name": "Planet 1",
                "population": 1000000,
                "climates": ["temperate"],
                "terrains": ["forest"],
            },
            {
                "external_id": "planet-2",
                "name": "Planet 2",
                "population": 2000000,
                "climates": ["arid"],
                "terrains": ["desert"],
            },
            {
                "external_id": "planet-3",
                "name": "Planet 3",
                "population": 3000000,
                "climates": ["frozen"],
                "terrains": ["tundra"],
            },
        ]

        created_planets = []
        for planet_data in planets_data:
            response = self.client.post(
                reverse("api:planet-list"), planet_data, format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            created_planets.append(response.data)

        # List all planets
        response = self.client.get(reverse("api:planet-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        # Verify all planets are in the list
        planet_names = [planet["name"] for planet in response.data]
        self.assertIn("Planet 1", planet_names)
        self.assertIn("Planet 2", planet_names)
        self.assertIn("Planet 3", planet_names)

        # Update one planet
        update_url = reverse("api:planet-detail", args=[created_planets[0]["id"]])
        response = self.client.patch(
            update_url, {"name": "Updated Planet 1"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the update
        response = self.client.get(update_url)
        self.assertEqual(response.data["name"], "Updated Planet 1")

    def test_serializer_validation_integration(self):
        """Test serializer validation in the context of API requests."""
        # Test invalid data
        invalid_data = {
            "name": "",  # Invalid: empty name
            "population": -1000,  # Invalid: negative population
            "climates": ["temperate"],
            "terrains": ["forest"],
        }

        response = self.client.post(
            reverse("api:planet-list"), invalid_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertIn("population", response.data)

        # Test valid data
        valid_data = {
            "name": "Valid Planet",
            "population": 1000000,
            "climates": ["temperate"],
            "terrains": ["forest"],
        }

        response = self.client.post(
            reverse("api:planet-list"), valid_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_model_methods_integration(self):
        """Test model methods in the context of API operations."""
        # Create a planet
        response = self.client.post(
            reverse("api:planet-list"), self.planet_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        planet_id = response.data["id"]

        # Retrieve and verify the planet data
        response = self.client.get(reverse("api:planet-detail", args=[planet_id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify climates and terrains are properly serialized
        self.assertEqual(response.data["climates"], ["temperate", "tropical"])
        self.assertEqual(response.data["terrains"], ["forest", "mountains"])

        # Update with new climates and terrains
        update_data = {
            "climates": ["hot", "dry"],
            "terrains": ["desert", "canyons", "mountains"],
        }
        response = self.client.patch(
            reverse("api:planet-detail", args=[planet_id]), update_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the update
        response = self.client.get(reverse("api:planet-detail", args=[planet_id]))
        self.assertEqual(response.data["climates"], ["hot", "dry"])
        self.assertEqual(response.data["terrains"], ["desert", "canyons", "mountains"])

    @patch("api.views.PlanetSyncService")
    def test_sync_integration(self, mock_sync_service):
        """Test sync functionality integration."""
        mock_service_instance = Mock()
        mock_sync_service.return_value = mock_service_instance
        mock_service_instance.sync_planets.return_value = {
            "created": 3,
            "updated": 1,
            "errors": 0,
            "total_processed": 4,
        }

        # Test full sync
        sync_url = reverse("api:planet-sync-planets")
        response = self.client.post(sync_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["action"], "full_sync")
        self.assertEqual(response.data["stats"]["created"], 3)
        mock_service_instance.sync_planets.assert_called_once()

        # Test sync status
        status_url = reverse("api:planet-sync-status")
        mock_service_instance.get_sync_status.return_value = {
            "total_planets_in_db": 5,
            "last_updated_planet": "Tatooine",
            "last_sync_time": "2023-01-01T00:00:00Z",
            "last_sync_stats": {},
        }

        response = self.client.get(status_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_planets_in_db"], 5)
        mock_service_instance.get_sync_status.assert_called_once()

    def test_error_handling_integration(self):
        """Test error handling in the API."""
        # Test accessing non-existent planet
        response = self.client.get(reverse("api:planet-detail", args=[99999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test updating non-existent planet
        response = self.client.put(
            reverse("api:planet-detail", args=[99999]), self.planet_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test deleting non-existent planet
        response = self.client.delete(reverse("api:planet-detail", args=[99999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_data_consistency_integration(self):
        """Test data consistency across different API operations."""
        # Create a planet
        response = self.client.post(
            reverse("api:planet-list"), self.planet_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        planet_id = response.data["id"]

        # Verify data in list view
        list_response = self.client.get(reverse("api:planet-list"))
        self.assertEqual(len(list_response.data), 1)
        list_planet = list_response.data[0]

        # Verify data in detail view
        detail_response = self.client.get(
            reverse("api:planet-detail", args=[planet_id])
        )
        detail_planet = detail_response.data

        # Both should have the same core data
        self.assertEqual(list_planet["name"], detail_planet["name"])
        self.assertEqual(list_planet["external_id"], detail_planet["external_id"])
        self.assertEqual(list_planet["population"], detail_planet["population"])
        self.assertEqual(list_planet["climates"], detail_planet["climates"])
        self.assertEqual(list_planet["terrains"], detail_planet["terrains"])

        # Detail view should have timestamps, list view should not
        self.assertIn("created_at", detail_planet)
        self.assertIn("updated_at", detail_planet)
        self.assertNotIn("created_at", list_planet)
        self.assertNotIn("updated_at", list_planet)
