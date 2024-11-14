from rest_framework import serializers
from .models import Client


class ClientSerializers(serializers.ModelSerializer):
    # fullname = serializers.CharField(read_only=True)
    parent_facility_name = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            "client_id",
            "fullname",
            "member_type",
            "insurance_id",
            "insurance_company",
            "corporate_id",
            "corporate_company",
            "parent_facility_name"
        ]

    def get_parent_facility_name(self, obj):
        facility = obj.parent_facility
        return facility.name if obj.parent_facility else None
