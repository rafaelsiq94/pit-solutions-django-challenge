from django.test import TestCase
from api.models import Planet


class PlanetModelTest(TestCase):
    """Test cases for the Planet model."""

    def setUp(self):
        """Set up test data."""
        self.planet_data = {
            "external_id": "test-123",
            "name": "Test Planet",
            "population": 1000000,
            "climates": ["temperate", "tropical"],
            "terrains": ["forest", "mountains"],
        }

    def test_planet_creation(self):
        """Test creating a planet with valid data."""
        planet = Planet.objects.create(**self.planet_data)

        self.assertEqual(planet.name, "Test Planet")
        self.assertEqual(planet.external_id, "test-123")
        self.assertEqual(planet.population, 1000000)
        self.assertEqual(planet.climates, ["temperate", "tropical"])
        self.assertEqual(planet.terrains, ["forest", "mountains"])
        self.assertIsNotNone(planet.created_at)
        self.assertIsNotNone(planet.updated_at)

    def test_planet_string_representation(self):
        """Test the string representation of a planet."""
        planet = Planet.objects.create(**self.planet_data)
        self.assertEqual(str(planet), "Test Planet")

    def test_planet_without_external_id(self):
        """Test creating a planet without external_id."""
        planet_data = self.planet_data.copy()
        del planet_data["external_id"]

        planet = Planet.objects.create(**planet_data)
        self.assertIsNone(planet.external_id)

    def test_set_climates_with_string(self):
        """Test setting climates with a comma-separated string."""
        planet = Planet.objects.create(**self.planet_data)
        planet.set_climates("hot, dry, windy")

        self.assertEqual(planet.climates, ["hot", "dry", "windy"])

    def test_set_climates_with_list(self):
        """Test setting climates with a list."""
        planet = Planet.objects.create(**self.planet_data)
        planet.set_climates(["cold", "frozen"])

        self.assertEqual(planet.climates, ["cold", "frozen"])

    def test_set_terrain_with_string(self):
        """Test setting terrains with a comma-separated string."""
        planet = Planet.objects.create(**self.planet_data)
        planet.set_terrain("desert, plains, hills")

        self.assertEqual(planet.terrains, ["desert", "plains", "hills"])

    def test_set_terrain_with_list(self):
        """Test setting terrains with a list."""
        planet = Planet.objects.create(**self.planet_data)
        planet.set_terrain(["ocean", "islands"])

        self.assertEqual(planet.terrains, ["ocean", "islands"])

    def test_get_climates_display(self):
        """Test getting climates as a display string."""
        planet = Planet.objects.create(**self.planet_data)
        self.assertEqual(planet.get_climates_display(), "temperate, tropical")

    def test_get_climates_display_empty(self):
        """Test getting climates display when climates is empty."""
        planet_data = self.planet_data.copy()
        planet_data["climates"] = []
        planet = Planet.objects.create(**planet_data)

        self.assertEqual(planet.get_climates_display(), "")

    def test_get_terrains_display(self):
        """Test getting terrains as a display string."""
        planet = Planet.objects.create(**self.planet_data)
        self.assertEqual(planet.get_terrains_display(), "forest, mountains")

    def test_get_terrains_display_empty(self):
        """Test getting terrains display when terrains is empty."""
        planet_data = self.planet_data.copy()
        planet_data["terrains"] = []
        planet = Planet.objects.create(**planet_data)

        self.assertEqual(planet.get_terrains_display(), "")

    def test_planet_timestamps(self):
        """Test that created_at and updated_at are automatically set."""
        planet = Planet.objects.create(**self.planet_data)

        self.assertIsNotNone(planet.created_at)
        self.assertIsNotNone(planet.updated_at)

        # Test that updated_at changes when planet is updated
        old_updated_at = planet.updated_at
        planet.name = "Updated Planet"
        planet.save()

        self.assertGreater(planet.updated_at, old_updated_at)

    def test_planet_external_id_index(self):
        """Test that external_id has a database index."""
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type='index' AND tbl_name='planets' AND sql LIKE '%external_id%'
            """
            )
            indexes = cursor.fetchall()

        # Should have at least one index on external_id
        self.assertGreater(len(indexes), 0)
