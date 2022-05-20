from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework import viewsets
from rest_framework.decorators import (
    action,
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import (
    ChangePasswordForgotSerializer,
    ChangePasswordSerializer,
    CodeWithEmailSerializer,
    FindEmailSerializer,
    RegisterUserSerializer,
    UpdateEmailSerializer,
    UserInfoSerializer,
)

User = get_user_model()


class RegisterAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        client = Client()
        jwt_response = client.post(
            path="/api/auth/get-token/",
            data={
                "email": serializer.data["email"],
                "password": request.data["password"],
            },
        ).json()

        return Response(
            {**serializer.data, **jwt_response},
            status=201,
            headers=headers,
        )


@api_view(["PATCH"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def change_my_email(request):
    new_email = request.data.get("email")
    serializer = UpdateEmailSerializer(request.user, {"email": new_email}, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"email": new_email}, 200)
    return Response(
        {"detail": serializer.errors.get("email", "Bad request!")},
        400,
    )


@api_view(["PATCH"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def change_my_password(request):
    old_passwd = request.data.get("password")
    new_password = request.data.get("new_password")
    confirmation_password = request.data.get("confirmation_password")
    serializer = ChangePasswordSerializer(
        request.user,
        {
            "password": old_passwd,
            "new_password": new_password,
            "confirmation_password": confirmation_password,
        },
        partial=True,
    )
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Successfully changed password."}, 200)
    return Response(
        {
            "detail": serializer.errors.get(
                "non_field_errors", "No blank fields allowed!"
            )
        },
        400,
    )


class ForgotPasswordViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == "change_password":
            return ChangePasswordForgotSerializer
        elif self.action == "send_reset_code":
            return CodeWithEmailSerializer
        else:
            return FindEmailSerializer

    @action(detail=False, methods=["get"])
    def send_email(self, request):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"success": f"Successfully sent a reset code to {user.email}."}, status=200
        )

    @action(detail=False, methods=["post"])
    def send_reset_code(self, request):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_token = serializer.save()
        return Response(
            {"session_token": f"{session_token}"},
            status=200,
        )

    @action(detail=False, methods=["patch"])
    def change_password(self, request):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {"success": f"Successfully changed password for {user.email}."}, status=200
        )


class UserInfoViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserInfoSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = [FormParser, JSONParser, MultiPartParser]

    @action(detail=False, methods=["get"])
    def get_current(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["put"])
    def update_current(self, request):
        serializer = self.get_serializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, 200)

    @action(detail=False, methods=["patch"])
    def partial_update_current(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, 200)
