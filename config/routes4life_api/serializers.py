import string

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import BaseUserManager
from django.core.mail import send_mail
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, Serializer

from .models import User
from .utils import ResetCodeManager, SessionTokenManager


class RegisterUserSerializer(ModelSerializer):
    password_2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "phone_number", "password", "password_2")
        extra_kwargs = {
            "password": {"write_only": True},
            "phone_number": {"required": False, "default": "+000000000"},
        }

    def create(self, validated_data):
        validated_data.pop("password_2")
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        print(validated_data)
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


# untested
class ChangePasswordForgotSerializer(Serializer):
    email = serializers.EmailField(required=True)
    session_token = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    new_password_2 = serializers.CharField(write_only=True, required=True)

    def validate(self, raw_data):
        norm_email = BaseUserManager.normalize_email(raw_data["email"])
        if not User.objects.filter(email=norm_email).exists():
            raise ValidationError({"email": f"No user {norm_email} was found."})
        self.instance = User.objects.get(email=norm_email)

        if len(raw_data["session_token"]) != 32 or not all(
            [
                (ch in (string.digits + string.ascii_letters))
                for ch in raw_data["session_token"]
            ]
        ):
            raise ValidationError({"session_token": "Invalid session token provided."})
        if not SessionTokenManager.try_use_token(norm_email, raw_data["session_token"]):
            raise ValidationError(
                {"session_token": "Session token has expired or it is incorrect."}
            )
        if raw_data["new_password"] != raw_data["new_password_2"]:
            raise serializers.ValidationError("New passwords don't match!")
        return raw_data

    def save(self):
        # instance will be provided during validation!!!
        self.instance.set_password(self.validated_data["new_password"])
        self.instance.save()
        return self.instance


# untested
class FindEmailSerializer(Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, raw_data):
        norm_email = BaseUserManager().normalize_email(raw_data["email"])
        if not User.objects.filter(email=norm_email).exists():
            raise ValidationError({"email": f"No user {norm_email} was found."})
        return raw_data

    def save(self):
        email = self.validated_data["email"]
        code_to_send = ResetCodeManager.get_or_create_code(email)
        send_mail(
            subject="Reset password code",
            message=f"Hi there, {email}."
            + f"Please enter this code to reset your password: {code_to_send}."
            + "Its TTL is only 2 minutes, so you should hurry!",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=True,
        )
        return User.objects.get(email=email)


# untested
class CodeWithEmailSerializer(Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True)

    def validate(self, raw_data):
        norm_email = BaseUserManager.normalize_email(raw_data["email"])
        if not User.objects.filter(email=norm_email).exists():
            raise ValidationError({"email": f"No user {norm_email} was found."})
        if len(raw_data["code"]) != 4 or not all(
            [(ch in string.digits) for ch in raw_data["code"]]
        ):
            raise ValidationError({"code": "Invalid code provided."})
        # here, submission code is deleted either way
        if not ResetCodeManager.try_use_code(norm_email, raw_data["code"]):
            raise ValidationError({"code": "Code has expired or it is incorrect."})
        return raw_data

    def save(self, **kwargs):
        """Overriden to return password reset session token."""
        email = self.validated_data["email"]
        session_token = SessionTokenManager.get_or_create_token(email)
        return session_token


class UserInfoSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phone_number")
        read_only_fields = ("email",)
        extra_kwargs = {"phone_number": {"required": False}}
