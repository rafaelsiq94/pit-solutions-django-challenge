from django.test import TestCase
from django.urls import reverse, resolve
from rest_framework.test import APIClient
from rest_framework import status


class URLTest(TestCase):
    """Test cases for URL routing."""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()

    def test_planet_list_url(self):
        """Test planet list URL resolution."""
        url = reverse("api:planet-list")
        self.assertEqual(url, "/api/planets/")

        # Test URL resolution
        resolver_match = resolve("/api/planets/")
        self.assertEqual(resolver_match.app_name, "api")
        self.assertEqual(resolver_match.url_name, "planet-list")

    def test_planet_detail_url(self):
        """Test planet detail URL resolution."""
        url = reverse("api:planet-detail", args=[1])
        self.assertEqual(url, "/api/planets/1/")

        # Test URL resolution
        resolver_match = resolve("/api/planets/1/")
        self.assertEqual(resolver_match.app_name, "api")
        self.assertEqual(resolver_match.url_name, "planet-detail")
        self.assertEqual(resolver_match.kwargs["pk"], "1")

    def test_planet_sync_url(self):
        """Test planet sync URL resolution."""
        url = reverse("api:planet-sync-planets")
        self.assertEqual(url, "/api/planets/sync/")

        # Test URL resolution
        resolver_match = resolve("/api/planets/sync/")
        self.assertEqual(resolver_match.app_name, "api")
        self.assertEqual(resolver_match.url_name, "planet-sync-planets")

    def test_planet_sync_status_url(self):
        """Test planet sync status URL resolution."""
        url = reverse("api:planet-sync-status")
        self.assertEqual(url, "/api/planets/sync-status/")

        # Test URL resolution
        resolver_match = resolve("/api/planets/sync-status/")
        self.assertEqual(resolver_match.app_name, "api")
        self.assertEqual(resolver_match.url_name, "planet-sync-status")

    def test_url_patterns_accessible(self):
        """Test that all URL patterns are accessible."""
        # Test list endpoint
        response = self.client.get("/api/planets/")
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test detail endpoint (should return 404 for non-existent planet)
        response = self.client.get("/api/planets/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test sync endpoint
        response = self.client.post("/api/planets/sync/")
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Test sync status endpoint
        response = self.client.get("/api/planets/sync-status/")
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_url_methods_allowed(self):
        """Test that URL patterns allow correct HTTP methods."""
        # Test list endpoint methods
        response = self.client.get("/api/planets/")
        self.assertNotEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post("/api/planets/", {}, format="json")
        self.assertNotEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Test detail endpoint methods
        response = self.client.get("/api/planets/99999/")
        self.assertNotEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.put("/api/planets/99999/", {}, format="json")
        self.assertNotEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch("/api/planets/99999/", {}, format="json")
        self.assertNotEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.delete("/api/planets/99999/")
        self.assertNotEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Test sync endpoint methods
        response = self.client.post("/api/planets/sync/")
        self.assertNotEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Sync endpoint should not allow GET
        response = self.client.get("/api/planets/sync/")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Test sync status endpoint methods
        response = self.client.get("/api/planets/sync-status/")
        self.assertNotEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Sync status endpoint should not allow POST
        response = self.client.post("/api/planets/sync-status/")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_url_namespace(self):
        """Test that URLs are properly namespaced."""
        # Test that URLs are in the 'api' namespace
        list_url = reverse("api:planet-list")
        self.assertIn("/api/", list_url)

        detail_url = reverse("api:planet-detail", args=[1])
        self.assertIn("/api/", detail_url)

        sync_url = reverse("api:planet-sync-planets")
        self.assertIn("/api/", sync_url)

        sync_status_url = reverse("api:planet-sync-status")
        self.assertIn("/api/", sync_status_url)

    def test_url_parameters(self):
        """Test URL parameter handling."""
        # Test different planet IDs
        for planet_id in [1, 123, 99999]:
            url = reverse("api:planet-detail", args=[planet_id])
            self.assertEqual(url, f"/api/planets/{planet_id}/")

            resolver_match = resolve(f"/api/planets/{planet_id}/")
            self.assertEqual(resolver_match.kwargs["pk"], str(planet_id))

    def test_url_trailing_slashes(self):
        """Test URL trailing slash handling."""
        # Test that URLs have proper trailing slashes
        list_url = reverse("api:planet-list")
        self.assertTrue(list_url.endswith("/"))

        detail_url = reverse("api:planet-detail", args=[1])
        self.assertTrue(detail_url.endswith("/"))

        sync_url = reverse("api:planet-sync-planets")
        self.assertTrue(sync_url.endswith("/"))

        sync_status_url = reverse("api:planet-sync-status")
        self.assertTrue(sync_status_url.endswith("/"))

    def test_url_reverse_consistency(self):
        """Test that URL reverse and resolve are consistent."""
        # Test list URL
        list_url = reverse("api:planet-list")
        resolver_match = resolve(list_url)
        self.assertEqual(resolver_match.url_name, "planet-list")

        # Test detail URL
        detail_url = reverse("api:planet-detail", args=[1])
        resolver_match = resolve(detail_url)
        self.assertEqual(resolver_match.url_name, "planet-detail")

        # Test sync URL
        sync_url = reverse("api:planet-sync-planets")
        resolver_match = resolve(sync_url)
        self.assertEqual(resolver_match.url_name, "planet-sync-planets")

        # Test sync status URL
        sync_status_url = reverse("api:planet-sync-status")
        resolver_match = resolve(sync_status_url)
        self.assertEqual(resolver_match.url_name, "planet-sync-status")
