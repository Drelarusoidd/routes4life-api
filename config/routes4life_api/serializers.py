from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import User


class RegisterUserSerializer(ModelSerializer):
    password_2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "phone_number", "password", "password_2")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data.pop("password_2")
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        return User.objects.create_user(email, password, **validated_data)

    def validate(self, raw_data):
        if raw_data["password"] != raw_data["password_2"]:
            raise serializers.ValidationError("Passwords don't match!")
        return raw_data


class UpdateEmailSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        kwargs["partial"] = True
        super(UpdateEmailSerializer, self).__init__(*args, **kwargs)


class ChangePasswordSerializer(ModelSerializer):
    new_password = serializers.CharField(write_only=True)
    new_password_2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("password", "new_password", "new_password_2")
        extra_kwargs = {"password": {"write_only": True}}

    def __init__(self, *args, **kwargs):
        kwargs["partial"] = True
        super(ChangePasswordSerializer, self).__init__(*args, **kwargs)

    def validate(self, raw_data):
        if check_password(raw_data["password"], self.instance.password) is False:
            raise serializers.ValidationError("Old password is incorrect!")
        if raw_data["new_password"] != raw_data["new_password_2"]:
            raise serializers.ValidationError("New passwords don't match!")
        return raw_data

    def save(self):
        self.instance.set_password(self.validated_data["new_password"])
        self.instance.save()
        return self.instance


class UserInfoSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phone_number")
        read_only_fields = ("email",)
