from django.test import TestCase
from unittest.mock import patch, Mock
from api.models import Planet
from api.services.graphql_client import GraphQLClient, StarWarsGraphQLClient
from api.services.data_generator import PlanetDataGenerator
from api.services.sync_service import PlanetSyncService
import requests


class GraphQLClientTest(TestCase):
    """Test cases for GraphQLClient."""

    @patch("requests.Session")
    def test_successful_query(self, mock_session_class):
        """Test successful GraphQL query."""
        mock_response = Mock()
        mock_response.json.return_value = {"data": {"test": "value"}}
        mock_response.raise_for_status.return_value = None

        mock_session = Mock()
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        # Create client after patching
        client = GraphQLClient("https://test-api.com/graphql")
        result = client.query("query { test }")

        self.assertEqual(result, {"test": "value"})
        mock_session.post.assert_called_once()

    @patch("requests.Session")
    @patch("api.services.graphql_client.logger")
    def test_query_with_errors(self, mock_logger, mock_session_class):
        """Test GraphQL query with errors in response."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": None,
            "errors": [{"message": "Test error"}],
        }
        mock_response.raise_for_status.return_value = None

        mock_session = Mock()
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        # Create client after patching
        client = GraphQLClient("https://test-api.com/graphql")

        with self.assertRaises(ValueError) as context:
            client.query("query { test }")

        self.assertIn("Test error", str(context.exception))

    @patch("requests.Session")
    @patch("api.services.graphql_client.logger")
    def test_request_exception(self, mock_logger, mock_session_class):
        """Test handling of request exceptions."""
        mock_session = Mock()
        mock_session.post.side_effect = requests.RequestException("Network error")
        mock_session_class.return_value = mock_session

        # Create client after patching
        client = GraphQLClient("https://test-api.com/graphql")

        with self.assertRaises(requests.RequestException):
            client.query("query { test }")

    @patch("requests.Session")
    def test_query_with_variables(self, mock_session_class):
        """Test GraphQL query with variables."""
        mock_response = Mock()
        mock_response.json.return_value = {"data": {"test": "value"}}
        mock_response.raise_for_status.return_value = None

        mock_session = Mock()
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        # Create client after patching
        client = GraphQLClient("https://test-api.com/graphql")

        variables = {"id": "123"}
        client.query("query { test }", variables)

        # Check that variables were included in the request
        call_args = mock_session.post.call_args
        self.assertEqual(call_args[1]["json"]["variables"], variables)


class StarWarsGraphQLClientTest(TestCase):
    """Test cases for StarWarsGraphQLClient."""

    def setUp(self):
        """Set up test data."""
        self.client = StarWarsGraphQLClient()

    def test_client_initialization(self):
        """Test client initialization with correct endpoint."""
        self.assertEqual(self.client.endpoint_url, "https://graphql.org/graphql")
        self.assertIn("Content-Type", self.client.headers)
        self.assertEqual(self.client.headers["Content-Type"], "application/json")

    def test_get_planets_query(self):
        """Test that planets query is properly formatted."""
        query = self.client.get_planets_query()

        self.assertIn("query GetPlanets", query)
        self.assertIn("allPlanets", query)
        self.assertIn("planets", query)
        self.assertIn("id", query)
        self.assertIn("name", query)
        self.assertIn("population", query)
        self.assertIn("climates", query)
        self.assertIn("terrains", query)

    @patch.object(GraphQLClient, "query")
    def test_fetch_planets(self, mock_query):
        """Test fetching planets from the API."""
        mock_query.return_value = {
            "allPlanets": {
                "planets": [{"id": "1", "name": "Tatooine", "population": 200000}]
            }
        }

        result = self.client.fetch_planets()

        self.assertEqual(result["allPlanets"]["planets"][0]["name"], "Tatooine")
        mock_query.assert_called_once()


class PlanetDataGeneratorTest(TestCase):
    """Test cases for PlanetDataGenerator."""

    def test_generate_population(self):
        """Test population generation."""
        population = PlanetDataGenerator.generate_population()

        self.assertIsInstance(population, int)
        self.assertGreater(population, 0)
        # Population should be divisible by 1000
        self.assertEqual(population % 1000, 0)

    def test_generate_climates(self):
        """Test climate generation."""
        climates = PlanetDataGenerator.generate_climates()

        self.assertIsInstance(climates, list)
        self.assertGreater(len(climates), 0)
        self.assertLessEqual(len(climates), 3)

        # All climates should be from the predefined list
        for climate in climates:
            self.assertIn(climate, PlanetDataGenerator.CLIMATE_TYPES)

    def test_generate_climates_with_count(self):
        """Test climate generation with specific count."""
        count = 2
        climates = PlanetDataGenerator.generate_climates(count)

        self.assertEqual(len(climates), count)
        self.assertEqual(len(set(climates)), count)  # No duplicates

    def test_generate_terrains(self):
        """Test terrain generation."""
        terrains = PlanetDataGenerator.generate_terrains()

        self.assertIsInstance(terrains, list)
        self.assertGreaterEqual(len(terrains), 2)
        self.assertLessEqual(len(terrains), 4)

        # All terrains should be from the predefined list
        for terrain in terrains:
            self.assertIn(terrain, PlanetDataGenerator.TERRAIN_TYPES)

    def test_generate_terrains_with_count(self):
        """Test terrain generation with specific count."""
        count = 3
        terrains = PlanetDataGenerator.generate_terrains(count)

        self.assertEqual(len(terrains), count)
        self.assertEqual(len(set(terrains)), count)  # No duplicates

    def test_generate_planet_data_complete(self):
        """Test generating planet data with complete original data."""
        original_data = {
            "id": "test-123",
            "name": "Test Planet",
            "population": 1000000,
            "climates": ["temperate"],
            "terrains": ["forest"],
        }

        result = PlanetDataGenerator.generate_planet_data("Test Planet", original_data)

        # Should return original data unchanged
        self.assertEqual(result, original_data)

    def test_generate_planet_data_missing_population(self):
        """Test generating planet data with missing population."""
        original_data = {
            "id": "test-123",
            "name": "Test Planet",
            "population": None,
            "climates": ["temperate"],
            "terrains": ["forest"],
        }

        result = PlanetDataGenerator.generate_planet_data("Test Planet", original_data)

        self.assertIsNotNone(result["population"])
        self.assertGreater(result["population"], 0)
        self.assertEqual(result["climates"], ["temperate"])
        self.assertEqual(result["terrains"], ["forest"])

    def test_generate_planet_data_missing_climates(self):
        """Test generating planet data with missing climates."""
        original_data = {
            "id": "test-123",
            "name": "Test Planet",
            "population": 1000000,
            "climates": None,
            "terrains": ["forest"],
        }

        result = PlanetDataGenerator.generate_planet_data("Test Planet", original_data)

        self.assertEqual(result["population"], 1000000)
        self.assertIsInstance(result["climates"], list)
        self.assertGreater(len(result["climates"]), 0)
        self.assertEqual(result["terrains"], ["forest"])

    def test_generate_planet_data_missing_terrains(self):
        """Test generating planet data with missing terrains."""
        original_data = {
            "id": "test-123",
            "name": "Test Planet",
            "population": 1000000,
            "climates": ["temperate"],
            "terrains": None,
        }

        result = PlanetDataGenerator.generate_planet_data("Test Planet", original_data)

        self.assertEqual(result["population"], 1000000)
        self.assertEqual(result["climates"], ["temperate"])
        self.assertIsInstance(result["terrains"], list)
        self.assertGreaterEqual(len(result["terrains"]), 2)

    def test_generate_planet_data_all_missing(self):
        """Test generating planet data with all optional fields missing."""
        original_data = {
            "id": "test-123",
            "name": "Test Planet",
            "population": None,
            "climates": None,
            "terrains": None,
        }

        result = PlanetDataGenerator.generate_planet_data("Test Planet", original_data)

        self.assertIsNotNone(result["population"])
        self.assertGreater(result["population"], 0)
        self.assertIsInstance(result["climates"], list)
        self.assertGreater(len(result["climates"]), 0)
        self.assertIsInstance(result["terrains"], list)
        self.assertGreaterEqual(len(result["terrains"]), 2)


class PlanetSyncServiceTest(TestCase):
    """Test cases for PlanetSyncService."""

    def setUp(self):
        """Set up test data."""
        self.sync_service = PlanetSyncService()

    def test_service_initialization(self):
        """Test service initialization."""
        self.assertIsNotNone(self.sync_service.client)
        self.assertEqual(self.sync_service.stats["created"], 0)
        self.assertEqual(self.sync_service.stats["updated"], 0)
        self.assertEqual(self.sync_service.stats["errors"], 0)
        self.assertEqual(self.sync_service.stats["total_processed"], 0)

    def test_transform_planet_data(self):
        """Test planet data transformation."""
        planet_data = {
            "id": "test-123",
            "name": "Test Planet",
            "population": 1000000,
            "climates": ["temperate"],
            "terrains": ["forest"],
        }

        result = self.sync_service._transform_planet_data(planet_data)

        self.assertEqual(result["external_id"], "test-123")
        self.assertEqual(result["name"], "Test Planet")
        self.assertEqual(result["population"], 1000000)
        self.assertEqual(result["climates"], ["temperate"])
        self.assertEqual(result["terrains"], ["forest"])

    def test_transform_planet_data_with_missing_fields(self):
        """Test planet data transformation with missing fields."""
        planet_data = {
            "id": "test-123",
            "name": "Test Planet",
            "population": None,
            "climates": None,
            "terrains": None,
        }

        result = self.sync_service._transform_planet_data(planet_data)

        self.assertEqual(result["external_id"], "test-123")
        self.assertEqual(result["name"], "Test Planet")
        self.assertIsNotNone(result["population"])
        self.assertIsInstance(result["climates"], list)
        self.assertIsInstance(result["terrains"], list)

    def test_update_or_create_planet_new(self):
        """Test creating a new planet."""
        planet_data = {
            "external_id": "new-123",
            "name": "New Planet",
            "population": 2000000,
            "climates": ["arid"],
            "terrains": ["desert"],
        }

        planet, created = self.sync_service._update_or_create_planet(planet_data)

        self.assertTrue(created)
        self.assertEqual(planet.name, "New Planet")
        self.assertEqual(planet.external_id, "new-123")
        self.assertEqual(self.sync_service.stats["created"], 1)

    def test_update_or_create_planet_existing(self):
        """Test updating an existing planet."""
        # Create a planet first
        Planet.objects.create(
            external_id="existing-123",
            name="Existing Planet",
            population=1000000,
            climates=["temperate"],
            terrains=["forest"],
        )

        planet_data = {
            "external_id": "existing-123",
            "name": "Updated Planet",
            "population": 3000000,
            "climates": ["frozen"],
            "terrains": ["tundra"],
        }

        planet, created = self.sync_service._update_or_create_planet(planet_data)

        self.assertFalse(created)
        self.assertEqual(planet.name, "Updated Planet")
        self.assertEqual(planet.population, 3000000)
        self.assertEqual(self.sync_service.stats["updated"], 1)

    @patch.object(PlanetSyncService, "_update_or_create_planet")
    @patch.object(StarWarsGraphQLClient, "fetch_planets")
    @patch("api.services.sync_service.logger")
    def test_sync_planets_success(self, mock_logger, mock_fetch_planets, mock_update_create):
        """Test successful planet synchronization."""
        mock_fetch_planets.return_value = {
            "allPlanets": {
                "planets": [
                    {"id": "1", "name": "Tatooine", "population": 200000},
                    {"id": "2", "name": "Alderaan", "population": 2000000000},
                ]
            }
        }

        # Mock the _update_or_create_planet method to update stats
        def mock_update_create_side_effect(planet_data):
            # Simulate the stats update that happens in the real method
            self.sync_service.stats["created"] += 1
            return (Mock(), True)  # (planet, created)

        mock_update_create.side_effect = mock_update_create_side_effect

        stats = self.sync_service.sync_planets()

        self.assertEqual(stats["total_processed"], 2)
        self.assertEqual(stats["created"], 2)
        self.assertEqual(stats["errors"], 0)
        mock_fetch_planets.assert_called_once()
        self.assertEqual(mock_update_create.call_count, 2)

    @patch.object(StarWarsGraphQLClient, "fetch_planets")
    @patch("api.services.sync_service.logger")
    def test_sync_planets_no_planets(self, mock_logger, mock_fetch_planets):
        """Test synchronization when no planets are returned."""
        mock_fetch_planets.return_value = {"allPlanets": {"planets": []}}

        stats = self.sync_service.sync_planets()

        self.assertEqual(stats["total_processed"], 0)
        self.assertEqual(stats["created"], 0)
        self.assertEqual(stats["updated"], 0)
        self.assertEqual(stats["errors"], 0)

    @patch.object(StarWarsGraphQLClient, "fetch_planets")
    @patch("api.services.sync_service.logger")
    def test_sync_planets_api_error(self, mock_logger, mock_fetch_planets):
        """Test synchronization when API returns an error."""
        mock_fetch_planets.side_effect = Exception("API Error")

        with self.assertRaises(Exception):
            self.sync_service.sync_planets()

    def test_get_sync_status_empty_db(self):
        """Test getting sync status with empty database."""
        status_data = self.sync_service.get_sync_status()

        self.assertEqual(status_data["total_planets_in_db"], 0)
        self.assertIsNone(status_data["last_updated_planet"])
        self.assertIsNone(status_data["last_sync_time"])

    def test_get_sync_status_with_planets(self):
        """Test getting sync status with planets in database."""
        # Create a planet
        Planet.objects.create(
            external_id="test-123",
            name="Test Planet",
            population=1000000,
            climates=["temperate"],
            terrains=["forest"],
        )

        status_data = self.sync_service.get_sync_status()

        self.assertEqual(status_data["total_planets_in_db"], 1)
        self.assertEqual(status_data["last_updated_planet"], "Test Planet")
        self.assertIsNotNone(status_data["last_sync_time"])
        self.assertEqual(status_data["last_sync_stats"], self.sync_service.stats)
