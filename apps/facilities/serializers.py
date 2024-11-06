from rest_framework import serializers
from .models import Facility
from apps.inventory.serializers import InventoryItemSerializer


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = [
            "name",
            "staff_number",
            "city",
            "region",
            "country"
        ]
