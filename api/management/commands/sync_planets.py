from django.core.management.base import BaseCommand, CommandError
from api.services.sync_service import PlanetSyncService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Synchronize planets from GraphQL API to local database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--status",
            action="store_true",
            help="Show sync status without performing sync",
        )
        parser.add_argument(
            "--verbose", action="store_true", help="Enable verbose output"
        )

    def handle(self, *args, **options):
        if options["verbose"]:
            logging.getLogger().setLevel(logging.INFO)

        sync_service = PlanetSyncService()

        try:
            if options["status"]:
                self.show_status(sync_service)
                return

            self.sync_all_planets(sync_service)

        except Exception as e:
            raise CommandError(f"Sync failed: {e}")

    def show_status(self, sync_service):
        """Display current sync status."""
        status = sync_service.get_sync_status()

        self.stdout.write(self.style.SUCCESS("=== Planet Sync Status ==="))
        self.stdout.write(f"Total planets in database: {status['total_planets_in_db']}")
        self.stdout.write(
            f"Last updated planet: {status['last_updated_planet'] or 'None'}"
        )
        self.stdout.write(f"Last sync time: {status['last_sync_time'] or 'Never'}")

        if status["last_sync_stats"]:
            stats = status["last_sync_stats"]
            self.stdout.write(self.style.WARNING("Last sync statistics:"))
            self.stdout.write(f"  Created: {stats['created']}")
            self.stdout.write(f"  Updated: {stats['updated']}")
            self.stdout.write(f"  Errors: {stats['errors']}")
            self.stdout.write(f"  Total processed: {stats['total_processed']}")

    def sync_all_planets(self, sync_service):
        """Sync all planets."""
        self.stdout.write("Starting planet synchronization...")

        stats = sync_service.sync_planets()

        self.stdout.write(self.style.SUCCESS("=== Sync Completed ==="))
        self.stdout.write(f"Created: {stats['created']}")
        self.stdout.write(f"Updated: {stats['updated']}")
        self.stdout.write(f"Errors: {stats['errors']}")
        self.stdout.write(f"Total processed: {stats['total_processed']}")

        if stats["errors"] > 0:
            self.stdout.write(
                self.style.WARNING(f"Sync completed with {stats['errors']} errors")
            )
        else:
            self.stdout.write(self.style.SUCCESS("Sync completed successfully!"))
