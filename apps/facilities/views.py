from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import ValidationError
from apps.users.permissions import IsAdminUser, IsSuperUser, IsWarehouse
from .models import Facility
from .serializers import FacilitySerializer
from apps.users.models import User
from apps.users.serializers import UserSerializer


class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer
    permission_classes = [IsSuperUser]
    http_method_names = [m for m in viewsets.ModelViewSet.http_method_names if m != "put"]
    lookup_field = "slug"

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsSuperUser]
        else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        return super().perform_create(serializer)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    # @action(detail=True, methods=["GET"], permission_classes=[IsAdminUser | IsSuperUser])
    # def get_staff(self, request, pk=None):
    #     if request.user.is_superuser:
    #         staff = User.objects.filter(facility=pk)
    #         if staff:
    #             serializer = UserSerializer(staff, many=True)
    #             return Response(serializer.data, status=200)
    #         return Response("No staff found", status=404)
    #     else:
    #         facility_id = request.user.facility
    #         if facility_id == pk:
    #             staff = User.objects.filter(facility=facility_id)
    #             if staff:
    #                 serializer = UserSerializer(staff, many=True)
    #                 return Response(serializer.data, status=200)
    #             return Response("No staff found", status=404)
    #         else:
    #             raise PermissionDenied("You do not have permission to view staff in this facility")


