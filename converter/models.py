from django.db import models

class UnitType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Unit(models.Model):
    name = models.CharField(max_length=50)
    unit_type = models.ForeignKey(UnitType, on_delete=models.CASCADE)
    to_base_factor = models.FloatField()  # Conversion factor to base unit

    def __str__(self):
        return f"{self.name} ({self.unit_type.name})"