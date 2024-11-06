from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from django.utils import timezone


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["name", "email", "password", "facility", "is_admin", "is_superuser", "is_warehouse"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
