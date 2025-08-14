from rest_framework import serializers
from .models import Planet


class PlanetSerializer(serializers.ModelSerializer):
    """
    Serializer for Planet model.
    Handles serialization and deserialization of planet data.
    """

    class Meta:
        model = Planet
        fields = [
            "id",
            "external_id",
            "name",
            "population",
            "climates",
            "terrains",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PlanetListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for planet list views.
    Excludes timestamps for cleaner list responses.
    """

    class Meta:
        model = Planet
        fields = ["id", "external_id", "name", "population", "climates", "terrains"]
        read_only_fields = ["id"]


class PlanetCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating planets.
    Allows setting climates and terrains as strings or lists.
    """

    climates = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    terrains = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    external_id = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Planet
        fields = ["id", "external_id", "name", "population", "climates", "terrains"]
        read_only_fields = ["id"]

    def validate_population(self, value):
        """Validate population is non-negative."""
        if value < 0:
            raise serializers.ValidationError("Population cannot be negative.")
        return value

    def validate_name(self, value):
        """Validate planet name is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Planet name cannot be empty.")
        return value.strip()

    def validate_external_id(self, value):
        """Validate external_id is unique if provided."""
        if value:
            instance = getattr(self, 'instance', None)
            if Planet.objects.filter(external_id=value).exclude(pk=instance.pk if instance else None).exists():
                raise serializers.ValidationError("A planet with this external_id already exists.")
        return value
