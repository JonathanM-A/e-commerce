from rest_framework import serializers
from .models import Facility


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = [
            "id",
            "slug",
            "name",
            "staff_number",
            "city",
            "region",
            "country"
        ]
