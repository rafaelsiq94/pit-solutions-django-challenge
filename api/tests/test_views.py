from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, Mock
from api.models import Planet
from api import views


class PlanetViewSetTest(TestCase):
    """Test cases for PlanetViewSet."""

    def setUp(self):
        """Set up test data and client."""
        self.client = APIClient()
        self.planet = Planet.objects.create(
            external_id="test-123",
            name="Test Planet",
            population=1000000,
            climates=["temperate", "tropical"],
            terrains=["forest", "mountains"],
        )

    def test_list_planets(self):
        """Test listing all planets."""
        url = reverse("api:planet-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check pagination structure
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)

        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Test Planet")
        self.assertEqual(response.data["results"][0]["external_id"], "test-123")
        # Should not include timestamps in list view
        self.assertNotIn("created_at", response.data["results"][0])
        self.assertNotIn("updated_at", response.data["results"][0])

    def test_list_planets_pagination(self):
        """Test pagination functionality."""
        # Create multiple planets for pagination testing
        for i in range(25):  # More than the default page size of 20
            Planet.objects.create(
                external_id=f"test-{i}",
                name=f"Planet {i}",
                population=1000000 + i,
                climates=["temperate"],
                terrains=["forest"],
            )

        url = reverse("api:planet-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 26)  # 25 + 1 from setUp
        self.assertEqual(len(response.data["results"]), 20)  # Default page size
        self.assertIsNotNone(response.data["next"])
        self.assertIsNone(response.data["previous"])

        # Test second page
        response = self.client.get(response.data["next"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 6)  # Remaining items
        self.assertIsNone(response.data["next"])
        self.assertIsNotNone(response.data["previous"])

    def test_search_planets_by_name(self):
        """Test searching planets by name."""
        # Create planets with different names
        Planet.objects.create(
            external_id="tatooine-123",
            name="Tatooine",
            population=200000,
            climates=["arid"],
            terrains=["desert"],
        )
        Planet.objects.create(
            external_id="naboo-123",
            name="Naboo",
            population=4500000000,
            climates=["temperate"],
            terrains=["grassy hills", "swamps"],
        )
        Planet.objects.create(
            external_id="hoth-123",
            name="Hoth",
            population=0,
            climates=["frozen"],
            terrains=["tundra", "ice caves"],
        )

        # Test exact search
        url = reverse("api:planet-list")
        response = self.client.get(url, {"search": "Tatooine"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Tatooine")

        # Test partial search (case-insensitive)
        response = self.client.get(url, {"search": "tat"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Tatooine")

        # Test case-insensitive search
        response = self.client.get(url, {"search": "TATOOINE"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Tatooine")

        # Test search with no results
        response = self.client.get(url, {"search": "NonExistentPlanet"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(len(response.data["results"]), 0)

    def test_search_planets_empty_query(self):
        """Test search with empty query parameter."""
        url = reverse("api:planet-list")
        response = self.client.get(url, {"search": ""})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return all planets (no filtering)
        self.assertGreater(response.data["count"], 0)

    def test_list_planets_ordering(self):
        """Test that planets are ordered by name."""
        # Create planets with different names
        Planet.objects.create(
            external_id="z-planet",
            name="Zeta Planet",
            population=1000000,
            climates=["temperate"],
            terrains=["forest"],
        )
        Planet.objects.create(
            external_id="a-planet",
            name="Alpha Planet",
            population=1000000,
            climates=["temperate"],
            terrains=["forest"],
        )

        url = reverse("api:planet-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]

        # Check that planets are ordered by name
        planet_names = [planet["name"] for planet in results]
        self.assertEqual(planet_names, sorted(planet_names))

    def test_retrieve_planet(self):
        """Test retrieving a single planet."""
        url = reverse("api:planet-detail", args=[self.planet.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Planet")
        self.assertEqual(response.data["external_id"], "test-123")
        # Should include timestamps in detail view
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

    def test_create_planet(self):
        """Test creating a new planet."""
        url = reverse("api:planet-list")
        data = {
            "external_id": "new-123",
            "name": "New Planet",
            "population": 2000000,
            "climates": ["arid", "hot"],
            "terrains": ["desert", "canyons"],
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Planet")
        self.assertEqual(response.data["external_id"], "new-123")

        # Verify planet was created in database
        planet = Planet.objects.get(external_id="new-123")
        self.assertEqual(planet.name, "New Planet")

    def test_create_planet_invalid_data(self):
        """Test creating a planet with invalid data."""
        url = reverse("api:planet-list")
        data = {
            "name": "",  # Invalid: empty name
            "population": -1000,  # Invalid: negative population
            "climates": ["temperate"],
            "terrains": ["forest"],
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertIn("population", response.data)

    def test_update_planet(self):
        """Test updating a planet."""
        url = reverse("api:planet-detail", args=[self.planet.id])
        data = {
            "name": "Updated Planet",
            "population": 3000000,
            "climates": ["frozen", "cold"],
            "terrains": ["tundra", "glaciers"],
        }

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Planet")
        self.assertEqual(response.data["population"], 3000000)

        # Verify planet was updated in database
        self.planet.refresh_from_db()
        self.assertEqual(self.planet.name, "Updated Planet")

    def test_partial_update_planet(self):
        """Test partially updating a planet."""
        url = reverse("api:planet-detail", args=[self.planet.id])
        data = {
            "name": "Partially Updated Planet",
        }

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Partially Updated Planet")
        # Other fields should remain unchanged
        self.assertEqual(response.data["population"], 1000000)

        # Verify planet was updated in database
        self.planet.refresh_from_db()
        self.assertEqual(self.planet.name, "Partially Updated Planet")

    def test_delete_planet(self):
        """Test deleting a planet."""
        url = reverse("api:planet-detail", args=[self.planet.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify planet was deleted from database
        self.assertFalse(Planet.objects.filter(id=self.planet.id).exists())

    def test_planet_not_found(self):
        """Test accessing a non-existent planet."""
        url = reverse("api:planet-detail", args=[99999])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("api.views.PlanetSyncService")
    def test_sync_planets_full_sync(self, mock_sync_service):
        """Test full planet synchronization."""
        mock_service_instance = Mock()
        mock_sync_service.return_value = mock_service_instance
        mock_service_instance.sync_planets.return_value = {
            "created": 5,
            "updated": 2,
            "errors": 0,
            "total_processed": 7,
        }

        url = reverse("api:planet-sync-planets")
        response = self.client.post(url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["action"], "full_sync")
        self.assertEqual(response.data["stats"]["created"], 5)
        self.assertEqual(response.data["stats"]["updated"], 2)
        mock_service_instance.sync_planets.assert_called_once()

    @patch("api.views.PlanetSyncService")
    def test_sync_planets_single_planet(self, mock_sync_service):
        """Test syncing a single planet."""
        mock_service_instance = Mock()
        mock_sync_service.return_value = mock_service_instance

        # Mock the planet that would be returned
        mock_planet = Mock()
        mock_planet.name = "Tatooine"
        mock_service_instance.sync_single_planet.return_value = mock_planet

        url = reverse("api:planet-sync-planets")
        data = {"planet_id": "test-123"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["action"], "single_sync")
        self.assertEqual(response.data["planet_id"], "test-123")
        self.assertEqual(
            response.data["message"], "Successfully synced planet: Tatooine"
        )
        mock_service_instance.sync_single_planet.assert_called_once_with("test-123")

    @patch("api.views.PlanetSyncService")
    def test_sync_planets_single_planet_failed(self, mock_sync_service):
        """Test syncing a single planet that fails."""
        mock_service_instance = Mock()
        mock_sync_service.return_value = mock_service_instance
        mock_service_instance.sync_single_planet.return_value = None

        url = reverse("api:planet-sync-planets")
        data = {"planet_id": "invalid-123"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        mock_service_instance.sync_single_planet.assert_called_once_with("invalid-123")

    @patch("api.views.PlanetSyncService")
    @patch("api.services.sync_service.logger")
    @patch("api.views.logger")
    def test_sync_planets_exception(
        self, mock_views_logger, mock_logger, mock_sync_service
    ):
        """Test sync planets when an exception occurs."""
        mock_service_instance = Mock()
        mock_sync_service.return_value = mock_service_instance
        mock_service_instance.sync_planets.side_effect = Exception("API Error")

        url = reverse("api:planet-sync-planets")
        response = self.client.post(url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)
        self.assertIn("API Error", response.data["error"])

    @patch("api.views.PlanetSyncService")
    def test_sync_status(self, mock_sync_service):
        """Test getting sync status."""
        mock_service_instance = Mock()
        mock_sync_service.return_value = mock_service_instance
        mock_service_instance.get_sync_status.return_value = {
            "total_planets_in_db": 1,
            "last_updated_planet": "Test Planet",
            "last_sync_time": "2023-01-01T00:00:00Z",
            "last_sync_stats": {
                "created": 1,
                "updated": 0,
                "errors": 0,
                "total_processed": 1,
            },
        }

        url = reverse("api:planet-sync-status")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_planets_in_db"], 1)
        self.assertEqual(response.data["last_updated_planet"], "Test Planet")
        mock_service_instance.get_sync_status.assert_called_once()

    @patch("api.views.PlanetSyncService")
    @patch("api.services.sync_service.logger")
    @patch("api.views.logger")
    def test_sync_status_exception(
        self, mock_views_logger, mock_logger, mock_sync_service
    ):
        """Test sync status when an exception occurs."""
        mock_service_instance = Mock()
        mock_sync_service.return_value = mock_service_instance
        mock_service_instance.get_sync_status.side_effect = Exception("Status Error")

        url = reverse("api:planet-sync-status")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)

    def test_serializer_class_selection(self):
        """Test that the correct serializer is selected for each action."""
        viewset = views.PlanetViewSet()

        # Test list action
        viewset.action = "list"
        self.assertEqual(viewset.get_serializer_class(), views.PlanetListSerializer)

        # Test create action
        viewset.action = "create"
        self.assertEqual(
            viewset.get_serializer_class(), views.PlanetCreateUpdateSerializer
        )

        # Test update action
        viewset.action = "update"
        self.assertEqual(
            viewset.get_serializer_class(), views.PlanetCreateUpdateSerializer
        )

        # Test partial_update action
        viewset.action = "partial_update"
        self.assertEqual(
            viewset.get_serializer_class(), views.PlanetCreateUpdateSerializer
        )

        # Test retrieve action
        viewset.action = "retrieve"
        self.assertEqual(viewset.get_serializer_class(), views.PlanetSerializer)

    def test_permissions(self):
        """Test that the viewset allows any permissions."""
        viewset = views.PlanetViewSet()
        self.assertEqual(viewset.permission_classes, [views.AllowAny])
