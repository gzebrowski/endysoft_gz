from rest_framework import serializers

from .models import AppUser


class SignInSerializer(serializers.Serializer):
    password = serializers.CharField()
    email = serializers.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user = None

    def get_user(self):
        return self._user

    def validate(self, data):
        self._user = AppUser.check_credentials(email=data["email"], password=data["password"])
        if self._user:
            return data
        raise serializers.ValidationError("Wrong credentials")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ["id", "email", "first_name", "last_name"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["token"] = instance.user_auth_token
        return data


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = AppUser
        fields = ["email", "first_name", "last_name", "password"]

    def create(self, validated_data):
        user = AppUser.objects.create_user(is_active=True, **validated_data)
        return user
