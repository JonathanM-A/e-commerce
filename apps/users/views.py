from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework.serializers import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenBlacklistView
from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken
from django.core.exceptions import PermissionDenied
from django.db.models import F
from django.db import transaction
from .models import User
from .serializers import UserSerializer
from ..facilities.models import Facility
from .permissions import IsAdminUser, IsSuperUser

# Use generic Views
# Add reset password functionality
# Check how to send a mail

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related("facility")
    serializer_class = UserSerializer
    permission_classes = [IsSuperUser]

    filterset_fields = ["facility"]
    search_fields = ["name"]

    def get_permissions(self):
        if self.request.user.is_superuser:
            return super().get_permissions()
        if self.action in ["update", "partial_update"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    @transaction.atomic
    def perform_create(self, serializer):
        # Increment the staff_number of the facility the user is being added to
        if not self.request.user.is_superuser:
            # Admins can only create staff linked to their facility
            facility = self.request.user.facility
            serializer.validated_data["facility"] = facility
        else:
            # Superusers can create staff linked to any facility
            facility = serializer.validated_data.get("facility")

        # Validation: Superusers must specify a facility for non-superusers or non-warehouse
        if facility is None:
            if not (
                serializer.validated_data.get("is_superuser")
                or serializer.validated_data.get("is_warehouse")
            ):
                raise ValidationError("Facility must be provided")
        
        # Increment facility's staff_number if acility was set
        if facility:
            Facility.objects.filter(pk=facility.pk).update(staff_number=F("staff_number") + 1)
        
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        """
        Allow only superusers to update user info
        """
        if not self.request.user.is_superuser:
            raise PermissionDenied("Only superusers can update users")
        return super().perform_update(serializer)

    @action(detail=False, methods=["POST"], permission_classes=[IsAuthenticated])
    def change_password(self, request):

        user = request.user
        old_password = request.data.get("old password")
        new_password1 = request.data.get("new password")
        new_password2 = request.data.get("confirm password")

        if not user.check_password(old_password):
            return Response("Incorrect password", status=400)

        if old_password == new_password1:
            return Response(
                "New password cannot be the same as old password", status=400
            )

        if new_password1 == new_password2:
            user.set_password(new_password1)
            user.save()
            return Response("Password changed", status=200)
        return Response("Passwords do not match", status=400)
    
    # view for forgotten password


class LogoutView(TokenBlacklistView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        auth_token = request.headers.get("Authorization")
        if not auth_token:
            return Response("Token not provided", status=400)
        refresh_token = (
            auth_token.split(" ")[1] if auth_token.startswith("Bearer ") else None
        )
        if refresh_token:
            try:
                token = OutstandingToken.objects.get(token=refresh_token)
                BlacklistedToken.objects.create(token=token)
                return Response("Log out successful", status=200)
            except OutstandingToken.DoesNotExist:
                return Response("Invalid token", status=404)

        return Response("Not Authorised", status=401)
