from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import User


class RegisterUserSerializer(ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "phone_number", "password", "password2")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data.pop("password2")
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        return User.objects.create_user(email, password, **validated_data)

    def validate(self, raw_data):
        if raw_data["password"] != raw_data["password2"]:
            raise serializers.ValidationError("Passwords don't match!")
        return raw_data


class UpdateEmailSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        kwargs["partial"] = True
        super(UpdateEmailSerializer, self).__init__(*args, **kwargs)


class UserInfoSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phone_number")
        read_only_fields = ("email",)
