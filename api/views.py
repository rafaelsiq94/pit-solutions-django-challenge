from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Planet
from .serializers import (
    PlanetSerializer,
    PlanetListSerializer,
    PlanetCreateUpdateSerializer,
)
from .services.sync_service import PlanetSyncService
import logging

logger = logging.getLogger(__name__)


class PlanetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing planets.
    Provides CRUD operations and custom actions.
    """

    queryset = Planet.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == "list":
            return PlanetListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return PlanetCreateUpdateSerializer
        return PlanetSerializer

    @action(detail=False, methods=["POST"], url_path="sync")
    def sync_planets(self, request):
        """Trigger planet synchronization from GraphQL API."""
        try:
            sync_service = PlanetSyncService()

            planet_id = request.data.get("planet_id")

            if planet_id:
                planet = sync_service.sync_single_planet(planet_id)
                if planet:
                    return Response(
                        {
                            "message": f"Successfully synced planet: {planet.name}",
                            "planet_id": planet_id,
                            "action": "single_sync",
                        }
                    )
                else:
                    return Response(
                        {"error": f"Failed to sync planet: {planet_id}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                stats = sync_service.sync_planets()

                return Response(
                    {
                        "message": "Planet synchronization completed",
                        "stats": stats,
                        "action": "full_sync",
                    }
                )

        except Exception as e:
            logger.error(f"Error during planet sync: {e}")
            return Response(
                {"error": f"Sync failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["GET"], url_path="sync-status")
    def sync_status(self, request):
        """Get current synchronization status."""
        try:
            sync_service = PlanetSyncService()
            status_data = sync_service.get_sync_status()

            return Response(status_data)

        except Exception as e:
            logger.error(f"Error fetching sync status: {e}")
            return Response(
                {"error": "Failed to fetch sync status"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
