from django.db import models


class Planet(models.Model):
    class Meta:
        db_table = "planets"

    id = models.AutoField(primary_key=True)
    external_id = models.CharField(max_length=255, db_index=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    population = models.IntegerField()
    climates = models.JSONField(default=list)
    terrains = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def set_climates(self, climate_list):
        """Set climates as a list of strings"""
        if isinstance(climate_list, str):
            self.climates = [item.strip() for item in climate_list.split(',')]
        else:
            self.climates = climate_list

    def set_terrain(self, terrain_list):
        """Set terrains as a list of strings"""
        if isinstance(terrain_list, str):
            self.terrains = [item.strip() for item in terrain_list.split(',')]
        else:
            self.terrains = terrain_list

    def get_climates_display(self):
        """Get climates as a comma-separated string for display"""
        return ', '.join(self.climates) if self.climates else ''

    def get_terrains_display(self):
        """Get terrains as a comma-separated string for display"""
        return ', '.join(self.terrains) if self.terrains else ''
