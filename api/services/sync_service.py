import logging
from typing import Dict, Any
from django.db import transaction
from django.utils import timezone
from .graphql_client import StarWarsGraphQLClient
from .data_generator import PlanetDataGenerator
from ..models import Planet

logger = logging.getLogger(__name__)


class PlanetSyncService:
    """
    Service for synchronizing planet data from GraphQL API to local database.
    Handles data fetching, transformation, and database updates.
    """

    def __init__(self):
        self.client = StarWarsGraphQLClient()
        self.stats = {"created": 0, "updated": 0, "errors": 0, "total_processed": 0}

    def _transform_planet_data(self, planet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform GraphQL planet data to match our model structure.
        Generate fake data for null/missing values using PlanetDataGenerator.

        Args:
            planet_data: Raw planet data from GraphQL

        Returns:
            Transformed data ready for database with generated values for null fields
        """
        planet_name = planet_data.get("name", "Unknown Planet")

        complete_data = PlanetDataGenerator.generate_planet_data(
            planet_name, planet_data
        )

        return {
            "external_id": complete_data.get("id"),
            "name": complete_data.get("name", ""),
            "population": complete_data.get("population", 0),
            "climates": complete_data.get("climates", []),
            "terrains": complete_data.get("terrains", []),
        }

    def _update_or_create_planet(
        self, planet_data: Dict[str, Any]
    ) -> tuple[Planet, bool]:
        """
        Update existing planet or create new one.

        Args:
            planet_data: Transformed planet data

        Returns:
            Tuple of (planet_instance, created_boolean)
        """
        external_id = planet_data["external_id"]

        try:
            planet, created = Planet.objects.update_or_create(
                external_id=external_id,
                defaults={
                    "name": planet_data["name"],
                    "population": planet_data["population"],
                    "climates": planet_data["climates"],
                    "terrains": planet_data["terrains"],
                    "updated_at": timezone.now(),
                },
            )

            if created:
                self.stats["created"] += 1
                logger.info(f"Created planet: {planet.name} (External ID: {external_id})")
            else:
                self.stats["updated"] += 1
                logger.info(f"Updated planet: {planet.name} (External ID: {external_id})")

            return planet, created

        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Error processing planet {external_id}: {e}")
            raise

    def sync_planets(self) -> Dict[str, int]:
        """
        Synchronize all planets from GraphQL API to local database.

        Returns:
            Dictionary with sync statistics
        """
        logger.info("Starting planet synchronization...")

        self.stats = {"created": 0, "updated": 0, "errors": 0, "total_processed": 0}

        try:
            response_data = self.client.fetch_planets()

            all_planets = response_data.get("allPlanets", {})
            planets = all_planets.get("planets", [])
            if not planets:
                logger.warning("No planets returned from API")

            with transaction.atomic():
                for planet_data in planets:
                    try:
                        transformed_data = self._transform_planet_data(planet_data)
                        self._update_or_create_planet(transformed_data)
                        self.stats["total_processed"] += 1

                    except Exception as e:
                        logger.error(f"Failed to process planet: {e}")
                        self.stats["errors"] += 1
                        continue

            logger.info(f"Processed batch: {len(planets)} planets")

            logger.info(f"Planet synchronization completed. Stats: {self.stats}")
            return self.stats

        except Exception as e:
            logger.error(f"Planet synchronization failed: {e}")
            raise

    def get_sync_status(self) -> Dict[str, Any]:
        """
        Get current synchronization status and statistics.

        Returns:
            Dictionary with sync status information
        """
        total_planets = Planet.objects.count()
        last_sync = Planet.objects.order_by("-updated_at").first()

        return {
            "total_planets_in_db": total_planets,
            "last_updated_planet": last_sync.name if last_sync else None,
            "last_sync_time": last_sync.updated_at if last_sync else None,
            "last_sync_stats": self.stats,
        }
