from rest_framework import serializers
from app_auth.models import AuthUser

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, error_messages={
        "min_length": "Password must be at least 6 characters long."
    })
    user_type = serializers.ChoiceField(choices=AuthUser.USER_TYPES, default='user')

    class Meta:
        model = AuthUser
        fields = ["id", "username", "password", "first_name", "last_name", "user_type"]
        extra_kwargs = {
            "password": {"write_only": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate_first_name(self, value):
        if len(value.strip()) < 1:
            raise serializers.ValidationError("First name cannot be empty.")
        return value

    def validate_last_name(self, value):
        if len(value.strip()) < 1:
            raise serializers.ValidationError("Last name cannot be empty.")
        return value

    def validate_username(self, value):
        if AuthUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken. Please choose another one.")
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        return value

    def create(self, validated_data):
        user = AuthUser.objects.create_user(**validated_data)
        return user
