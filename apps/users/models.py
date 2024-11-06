from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from apps.facilities.models import Facility


class UserManager(BaseUserManager):
    def create_user(self, email, name, password, facility, is_warehouse=False):
        if not email:
            raise ValueError("Users must have an email")
        if not name:
            raise ValueError("Users must have a first and last name")
        if not password:
            raise ValueError("Users must have a password")
        if not facility and not is_warehouse:
            raise ValueError("User must be linked to a facility")

        validate_password(password)

        facility_instance = Facility.objects.get(id=facility)
        if facility_instance:
            user = self.model(
                email=self.normalize_email(email),
                name=name,
                facility=facility_instance,
                is_warehouse=is_warehouse,
            )
            user.set_paassword(password)
            user.save()
            return user

    def create_superuser(self, email, name, password):
        if not email:
            raise ValueError("Users must have an email")
        if not name:
            raise ValueError("Users must have a first and last name")
        if not password:
            raise ValueError("Users must have a password")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )
        user.set_password(password)
        user.is_staff, user.is_admin, user.is_superuser = True, True, True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=254, unique=True, null=False)
    name = models.CharField(max_length=255, null=False)
    facility = models.ForeignKey(
        Facility, on_delete=models.CASCADE, null=True, related_name="staff"
    )
    is_warehouse = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(default=timezone.now)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        db_table = "users"
