from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from io import StringIO
from unittest.mock import patch, Mock
import subprocess
import sys


class SyncPlanetsCommandTest(TestCase):
    """Test cases for the sync_planets management command."""

    def setUp(self):
        """Set up test data."""
        self.out = StringIO()

    @patch("api.management.commands.sync_planets.PlanetSyncService")
    def test_sync_planets_success(self, mock_sync_service):
        """Test successful planet synchronization."""
        mock_service_instance = Mock()
        mock_sync_service.return_value = mock_service_instance
        mock_service_instance.sync_planets.return_value = {
            "created": 5,
            "updated": 2,
            "errors": 0,
            "total_processed": 7,
        }

        call_command("sync_planets", stdout=self.out)

        output = self.out.getvalue()
        self.assertIn("Starting planet synchronization...", output)
        self.assertIn("=== Sync Completed ===", output)
        self.assertIn("Created: 5", output)
        self.assertIn("Updated: 2", output)
        self.assertIn("Errors: 0", output)
        self.assertIn("Total processed: 7", output)
        self.assertIn("Sync completed successfully!", output)

        mock_service_instance.sync_planets.assert_called_once()

    @patch("api.management.commands.sync_planets.PlanetSyncService")
    def test_sync_planets_with_errors(self, mock_sync_service):
        """Test planet synchronization with errors."""
        mock_service_instance = Mock()
        mock_sync_service.return_value = mock_service_instance
        mock_service_instance.sync_planets.return_value = {
            "created": 3,
            "updated": 1,
            "errors": 2,
            "total_processed": 6,
        }

        call_command("sync_planets", stdout=self.out)

        output = self.out.getvalue()
        self.assertIn("Sync completed with 2 errors", output)
        self.assertIn("Errors: 2", output)

    @patch("api.management.commands.sync_planets.PlanetSyncService")
    def test_sync_planets_exception(self, mock_sync_service):
        """Test planet synchronization when an exception occurs."""
        mock_service_instance = Mock()
        mock_sync_service.return_value = mock_service_instance
        mock_service_instance.sync_planets.side_effect = Exception("API Error")

        with self.assertRaises(CommandError) as context:
            call_command("sync_planets", stdout=self.out)

        self.assertIn("API Error", str(context.exception))

    @patch("api.management.commands.sync_planets.PlanetSyncService")
    def test_sync_status_command(self, mock_sync_service):
        """Test sync status command."""
        mock_service_instance = Mock()
        mock_sync_service.return_value = mock_service_instance
        mock_service_instance.get_sync_status.return_value = {
            "total_planets_in_db": 10,
            "last_updated_planet": "Tatooine",
            "last_sync_time": "2023-01-01T00:00:00Z",
            "last_sync_stats": {
                "created": 5,
                "updated": 2,
                "errors": 0,
                "total_processed": 7,
            },
        }

        call_command("sync_planets", "--status", stdout=self.out)

        output = self.out.getvalue()
        self.assertIn("=== Planet Sync Status ===", output)
        self.assertIn("Total planets in database: 10", output)
        self.assertIn("Last updated planet: Tatooine", output)
        self.assertIn("Last sync time: 2023-01-01T00:00:00Z", output)

        # Should not call sync_planets when --status is used
        mock_service_instance.sync_planets.assert_not_called()
        mock_service_instance.get_sync_status.assert_called_once()

    @patch("api.management.commands.sync_planets.PlanetSyncService")
    def test_sync_status_empty_db(self, mock_sync_service):
        """Test sync status with empty database."""
        mock_service_instance = Mock()
        mock_sync_service.return_value = mock_service_instance
        mock_service_instance.get_sync_status.return_value = {
            "total_planets_in_db": 0,
            "last_updated_planet": None,
            "last_sync_time": None,
            "last_sync_stats": {},
        }

        call_command("sync_planets", "--status", stdout=self.out)

        output = self.out.getvalue()
        self.assertIn("Total planets in database: 0", output)
        self.assertIn("Last updated planet: None", output)
        self.assertIn("Last sync time: Never", output)

    @patch("api.management.commands.sync_planets.PlanetSyncService")
    def test_sync_planets_verbose(self, mock_sync_service):
        """Test planet synchronization with verbose output."""
        mock_service_instance = Mock()
        mock_sync_service.return_value = mock_service_instance
        mock_service_instance.sync_planets.return_value = {
            "created": 3,
            "updated": 1,
            "errors": 0,
            "total_processed": 4,
        }

        call_command("sync_planets", "--verbose", stdout=self.out)

        output = self.out.getvalue()
        self.assertIn("Starting planet synchronization...", output)
        self.assertIn("Sync completed successfully!", output)

        mock_service_instance.sync_planets.assert_called_once()

    @patch("api.management.commands.sync_planets.PlanetSyncService")
    def test_sync_planets_status_verbose(self, mock_sync_service):
        """Test sync status with verbose output."""
        mock_service_instance = Mock()
        mock_sync_service.return_value = mock_service_instance
        mock_service_instance.get_sync_status.return_value = {
            "total_planets_in_db": 5,
            "last_updated_planet": "Alderaan",
            "last_sync_time": "2023-01-01T00:00:00Z",
            "last_sync_stats": {},
        }

        call_command("sync_planets", "--status", "--verbose", stdout=self.out)

        output = self.out.getvalue()
        self.assertIn("=== Planet Sync Status ===", output)
        self.assertIn("Total planets in database: 5", output)
        self.assertIn("Last updated planet: Alderaan", output)

        # Should not call sync_planets when --status is used
        mock_service_instance.sync_planets.assert_not_called()
        mock_service_instance.get_sync_status.assert_called_once()

    def test_command_help(self):
        """Test command help text."""
        # Use subprocess to capture help output
        result = subprocess.run(
            [sys.executable, "manage.py", "sync_planets", "--help"],
            capture_output=True,
            text=True,
            cwd="/Users/rafael/Downloads/pit-solutions-django-challenge",
        )

        output = result.stdout + result.stderr
        self.assertIn("Synchronize planets from GraphQL API to local database", output)
        self.assertIn("--status", output)
        self.assertIn("--verbose", output)

    @patch("api.management.commands.sync_planets.PlanetSyncService")
    def test_sync_planets_no_planets_synced(self, mock_sync_service):
        """Test synchronization when no planets are synced."""
        mock_service_instance = Mock()
        mock_sync_service.return_value = mock_service_instance
        mock_service_instance.sync_planets.return_value = {
            "created": 0,
            "updated": 0,
            "errors": 0,
            "total_processed": 0,
        }

        call_command("sync_planets", stdout=self.out)

        output = self.out.getvalue()
        self.assertIn("Created: 0", output)
        self.assertIn("Updated: 0", output)
        self.assertIn("Errors: 0", output)
        self.assertIn("Total processed: 0", output)
        self.assertIn("Sync completed successfully!", output)

    @patch("api.management.commands.sync_planets.PlanetSyncService")
    def test_sync_status_exception(self, mock_sync_service):
        """Test sync status when an exception occurs."""
        mock_service_instance = Mock()
        mock_sync_service.return_value = mock_service_instance
        mock_service_instance.get_sync_status.side_effect = Exception("Status Error")

        with self.assertRaises(CommandError) as context:
            call_command("sync_planets", "--status", stdout=self.out)

        self.assertIn("Status Error", str(context.exception))
