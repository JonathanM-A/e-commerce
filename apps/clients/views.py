from django.db.models import Q, F
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .models import Client
from .serializers import ClientSerializers
from apps.users.permissions import IsAdminUser, IsSuperUser
from rest_framework.exceptions import PermissionDenied, ValidationError


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.select_related("parent_facility").all()
    serializer_class = ClientSerializers
    permission_classes = [IsSuperUser]
    search_fields = ["client_id", "fullname", "phone_number"]

    def get_permissions(self):
        if self.action in ["list", "retrieve", "partial_update"]:
            permission_classes = [IsAuthenticated]
            return [permission() for permission in permission_classes]
        return super().get_permissions()

    # modify perform_partial_update to allow only parent facility to update without needing OTP
    def perform_create(self, serializer):
        # client parent facility will be facility of creator
        user = self.request.user
        if not user.is_superuser:
            facility = user.facility
            serializer.save(facility=facility)
        else:
            serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        if user.is_superuser:
            facility = serializer.validated_data.get("facility")
            if not facility:
                raise ValidationError(
                    "Superusers must provide a facility for the client")
        else:
            serializer.validate_data["facility"] = user.facility
        super().perform_create(serializer)
