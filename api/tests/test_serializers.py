from django.test import TestCase
from api.models import Planet
from api.serializers import (
    PlanetSerializer,
    PlanetListSerializer,
    PlanetCreateUpdateSerializer,
)


class PlanetSerializerTest(TestCase):
    """Test cases for PlanetSerializer."""

    def setUp(self):
        """Set up test data."""
        self.planet = Planet.objects.create(
            external_id="test-123",
            name="Test Planet",
            population=1000000,
            climates=["temperate", "tropical"],
            terrains=["forest", "mountains"],
        )

    def test_planet_serialization(self):
        """Test serializing a planet to JSON."""
        serializer = PlanetSerializer(self.planet)
        data = serializer.data

        self.assertEqual(data["id"], self.planet.id)
        self.assertEqual(data["external_id"], "test-123")
        self.assertEqual(data["name"], "Test Planet")
        self.assertEqual(data["population"], 1000000)
        self.assertEqual(data["climates"], ["temperate", "tropical"])
        self.assertEqual(data["terrains"], ["forest", "mountains"])
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

    def test_planet_deserialization(self):
        """Test deserializing JSON to planet data."""
        data = {
            "external_id": "new-123",
            "name": "New Planet",
            "population": 2000000,
            "climates": ["arid", "hot"],
            "terrains": ["desert", "canyons"],
        }

        serializer = PlanetSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        planet_data = serializer.validated_data
        self.assertEqual(planet_data["external_id"], "new-123")
        self.assertEqual(planet_data["name"], "New Planet")
        self.assertEqual(planet_data["population"], 2000000)
        self.assertEqual(planet_data["climates"], ["arid", "hot"])
        self.assertEqual(planet_data["terrains"], ["desert", "canyons"])


class PlanetListSerializerTest(TestCase):
    """Test cases for PlanetListSerializer."""

    def setUp(self):
        """Set up test data."""
        self.planet = Planet.objects.create(
            external_id="test-123",
            name="Test Planet",
            population=1000000,
            climates=["temperate", "tropical"],
            terrains=["forest", "mountains"],
        )

    def test_planet_list_serialization(self):
        """Test serializing a planet for list view."""
        serializer = PlanetListSerializer(self.planet)
        data = serializer.data

        self.assertEqual(data["id"], self.planet.id)
        self.assertEqual(data["external_id"], "test-123")
        self.assertEqual(data["name"], "Test Planet")
        self.assertEqual(data["population"], 1000000)
        self.assertEqual(data["climates"], ["temperate", "tropical"])
        self.assertEqual(data["terrains"], ["forest", "mountains"])

        # Should not include timestamps
        self.assertNotIn("created_at", data)
        self.assertNotIn("updated_at", data)

    def test_planet_list_deserialization(self):
        """Test deserializing JSON for list view."""
        data = {
            "external_id": "new-123",
            "name": "New Planet",
            "population": 2000000,
            "climates": ["arid", "hot"],
            "terrains": ["desert", "canyons"],
        }

        serializer = PlanetListSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class PlanetCreateUpdateSerializerTest(TestCase):
    """Test cases for PlanetCreateUpdateSerializer."""

    def setUp(self):
        """Set up test data."""
        self.planet = Planet.objects.create(
            external_id="test-123",
            name="Test Planet",
            population=1000000,
            climates=["temperate", "tropical"],
            terrains=["forest", "mountains"],
        )

    def test_planet_create_serialization(self):
        """Test serializing a planet for create/update."""
        serializer = PlanetCreateUpdateSerializer(self.planet)
        data = serializer.data

        self.assertEqual(data["id"], self.planet.id)
        self.assertEqual(data["external_id"], "test-123")
        self.assertEqual(data["name"], "Test Planet")
        self.assertEqual(data["population"], 1000000)
        self.assertEqual(data["climates"], ["temperate", "tropical"])
        self.assertEqual(data["terrains"], ["forest", "mountains"])

    def test_planet_create_valid_data(self):
        """Test creating a planet with valid data."""
        data = {
            "external_id": "new-123",
            "name": "New Planet",
            "population": 2000000,
            "climates": ["arid", "hot"],
            "terrains": ["desert", "canyons"],
        }

        serializer = PlanetCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        planet = serializer.save()
        self.assertEqual(planet.name, "New Planet")
        self.assertEqual(planet.external_id, "new-123")
        self.assertEqual(planet.population, 2000000)

    def test_planet_create_without_external_id(self):
        """Test creating a planet without external_id."""
        data = {
            "name": "New Planet",
            "population": 2000000,
            "climates": ["arid", "hot"],
            "terrains": ["desert", "canyons"],
        }

        serializer = PlanetCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        planet = serializer.save()
        self.assertIsNone(planet.external_id)

    def test_planet_create_with_empty_climates_terrains(self):
        """Test creating a planet with empty climates and terrains."""
        data = {
            "name": "New Planet",
            "population": 2000000,
            "climates": [],
            "terrains": [],
        }

        serializer = PlanetCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        planet = serializer.save()
        self.assertEqual(planet.climates, [])
        self.assertEqual(planet.terrains, [])

    def test_planet_update(self):
        """Test updating an existing planet."""
        data = {
            "name": "Updated Planet",
            "population": 3000000,
            "climates": ["frozen", "cold"],
            "terrains": ["tundra", "glaciers"],
        }

        serializer = PlanetCreateUpdateSerializer(self.planet, data=data)
        self.assertTrue(serializer.is_valid())

        planet = serializer.save()
        self.assertEqual(planet.name, "Updated Planet")
        self.assertEqual(planet.population, 3000000)
        self.assertEqual(planet.climates, ["frozen", "cold"])
        self.assertEqual(planet.terrains, ["tundra", "glaciers"])

    def test_validate_population_negative(self):
        """Test validation of negative population."""
        data = {
            "name": "Test Planet",
            "population": -1000,
            "climates": ["temperate"],
            "terrains": ["forest"],
        }

        serializer = PlanetCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("population", serializer.errors)

    def test_validate_population_zero(self):
        """Test validation of zero population."""
        data = {
            "name": "Test Planet",
            "population": 0,
            "climates": ["temperate"],
            "terrains": ["forest"],
        }

        serializer = PlanetCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_name_empty(self):
        """Test validation of empty name."""
        data = {
            "name": "",
            "population": 1000000,
            "climates": ["temperate"],
            "terrains": ["forest"],
        }

        serializer = PlanetCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_validate_name_whitespace(self):
        """Test validation of name with only whitespace."""
        data = {
            "name": "   ",
            "population": 1000000,
            "climates": ["temperate"],
            "terrains": ["forest"],
        }

        serializer = PlanetCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_validate_name_stripped(self):
        """Test that name is stripped of whitespace."""
        data = {
            "name": "  Test Planet  ",
            "population": 1000000,
            "climates": ["temperate"],
            "terrains": ["forest"],
        }

        serializer = PlanetCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["name"], "Test Planet")

    def test_validate_external_id_unique(self):
        """Test validation of unique external_id."""
        # Create another planet with different external_id
        Planet.objects.create(
            external_id="existing-123",
            name="Existing Planet",
            population=1000000,
            climates=["temperate"],
            terrains=["forest"],
        )

        data = {
            "external_id": "existing-123",
            "name": "New Planet",
            "population": 2000000,
            "climates": ["arid"],
            "terrains": ["desert"],
        }

        serializer = PlanetCreateUpdateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("external_id", serializer.errors)

    def test_validate_external_id_update_same_planet(self):
        """Test that updating a planet with its own external_id is valid."""
        data = {
            "external_id": "test-123",  # Same as existing planet
            "name": "Updated Planet",
            "population": 2000000,
            "climates": ["arid"],
            "terrains": ["desert"],
        }

        serializer = PlanetCreateUpdateSerializer(self.planet, data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_external_id_blank_null(self):
        """Test validation of blank and null external_id."""
        data = {
            "external_id": "",
            "name": "Test Planet",
            "population": 1000000,
            "climates": ["temperate"],
            "terrains": ["forest"],
        }

        serializer = PlanetCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        data["external_id"] = None
        serializer = PlanetCreateUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
