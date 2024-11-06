from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class UserAdmin(BaseUserAdmin):
    ordering = ["email"]
    list_display = (
        "email",
        "name",
        "facility",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
        "last_login",
    )
    list_filter = ("facility", "is_active", "is_admin", "is_superuser")
    search_fields = ("email", "name")

    fieldsets = (
        (None, {"fields": ("email", "password", "facility")}),
        (("Personal Info"), {"fields": ("name",)}),
        (
            ("Permissions"),
            {"fields": ("is_active", "is_staff", "is_admin", "is_superuser")},
        ),
        (("Important dates"), {"fields": ("date_joined", "last_login")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "facility",
                    "password1",
                    "password2",
                    "is_admin",
                ),
            },
        ),
    )


admin.site.register(User, UserAdmin)
