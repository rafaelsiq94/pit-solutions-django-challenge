from faker import Faker
import random
from typing import List, Optional

fake = Faker()


class PlanetDataGenerator:
    """
    Generates fake data for planets when API data is null or missing.
    Uses Faker library to create believable planet characteristics.
    """

    CLIMATE_TYPES = [
        "temperate",
        "tropical",
        "arid",
        "frozen",
        "humid",
        "windy",
        "hot",
        "cold",
        "mild",
        "stormy",
        "clear",
        "cloudy",
        "rainy",
        "dry",
        "moist",
        "foggy",
        "misty",
        "hazy",
        "crisp",
        "muggy",
    ]

    TERRAIN_TYPES = [
        "desert",
        "forest",
        "rainforest",
        "grassland",
        "tundra",
        "mountains",
        "hills",
        "plains",
        "swamp",
        "jungle",
        "savanna",
        "steppe",
        "marsh",
        "volcanoes",
        "canyons",
        "valleys",
        "plateaus",
        "islands",
        "coastlines",
        "caves",
        "craters",
        "lakes",
        "rivers",
        "oceans",
        "glaciers",
        "cliffs",
    ]

    @classmethod
    def generate_population(cls) -> int:
        """
        Generate a random population.

        Returns:
            Random population number
        """
        population_ranges = [
            (1000, 10000),
            (10000, 100000),
            (100000, 1000000),
            (1000000, 10000000),
            (10000000, 100000000),
            (100000000, 1000000000),
            (1000000000, 10000000000),
        ]

        min_pop, max_pop = random.choice(population_ranges)

        population = random.randint(min_pop, max_pop)

        return (population // 1000) * 1000

    @classmethod
    def generate_climates(cls, count: Optional[int] = None) -> List[str]:
        """
        Generate random climate types for a planet.

        Args:
            count: Number of climates to generate (random if None)

        Returns:
            List of climate types
        """
        if count is None:
            count = random.randint(1, 3)

        return random.sample(cls.CLIMATE_TYPES, min(count, len(cls.CLIMATE_TYPES)))

    @classmethod
    def generate_terrains(cls, count: Optional[int] = None) -> List[str]:
        """
        Generate random terrain types for a planet.

        Args:
            count: Number of terrains to generate (random if None)

        Returns:
            List of terrain types
        """
        if count is None:
            count = random.randint(2, 4)

        return random.sample(cls.TERRAIN_TYPES, min(count, len(cls.TERRAIN_TYPES)))

    @classmethod
    def generate_planet_data(cls, planet_name: str, original_data: dict) -> dict:
        """
        Generate complete planet data, filling in null values with random fake data.

        Args:
            planet_name: Name of the planet
            original_data: Original data from API

        Returns:
            Complete planet data with generated values for null fields
        """
        generated_data = original_data.copy()

        if not original_data.get("population"):
            generated_data["population"] = cls.generate_population()

        if not original_data.get("climates"):
            generated_data["climates"] = cls.generate_climates()

        if not original_data.get("terrains"):
            generated_data["terrains"] = cls.generate_terrains()

        return generated_data
