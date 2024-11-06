from django.db import models
from django.utils import timezone


class Facility(models.Model):
    name = models.CharField(max_length=255, null=False)
    city = models.CharField(max_length=255, null=False)
    region = models.CharField(max_length=255, null=False)
    country = models.CharField(max_length=255, null=False)
    staff_number = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    date_added = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "facilities"

    def __str__(self):
        return f"{self.name}, {self.city.title()}"
