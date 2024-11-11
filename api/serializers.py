# api/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, InvestorProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "password")
        extra_kwargs = {"password": {"write_only": True}, "email": {"required": True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={"input_type": "password"})


class InvestorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestorProfile
        fields = (
            "id",
            "index",
            "name",
            "surname",
            "phone_prefix",
            "phone_number",
            "email",
            "amount_lost",
            "agree_to_be_called",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "index", "created_at", "updated_at")

    def validate_phone_prefix(self, value):
        if not value.startswith("+"):
            raise serializers.ValidationError("Phone prefix must start with '+'")
        return value

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits")
        return value
