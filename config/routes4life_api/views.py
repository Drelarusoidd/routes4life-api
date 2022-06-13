from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

# from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.decorators import (
    action,
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from routes4life_api.models import Place
from routes4life_api.permissions import IsSameUserOrReadonly
from routes4life_api.serializers import (
    AddPlaceImagesSerializer,
    ChangePasswordForgotSerializer,
    ChangePasswordSerializer,
    ClientValidatePlaceSerializer,
    CodeWithEmailSerializer,
    CreateUpdatePlaceSerializer,
    FindEmailSerializer,
    GetPlaceSerializer,
    RegisterUserSerializer,
    RemovePlaceImagesSerializer,
    UpdateEmailSerializer,
    UserInfoSerializer,
)
from routes4life_api.utils import convert_placedata_to_geojson

User = get_user_model()


class RegisterAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        user = serializer.instance
        access_token = str(AccessToken.for_user(user))
        refresh_token = str(RefreshToken.for_user(user))

        return Response(
            {**serializer.data, "access": access_token, "refresh": refresh_token},
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


class UserInfoViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=["get"])
    def get_current(self, request):
        serializer = UserInfoSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["patch"])
    def partial_update_current(self, request):
        change_pass_serializer = None
        if request.data.get("password") is not None:
            change_pass_serializer = ChangePasswordSerializer(
                request.user, data=request.data
            )
            change_pass_serializer.is_valid(raise_exception=True)
        serializer = UserInfoSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        # if everything is fine, we apply all changes at once
        if change_pass_serializer is not None:
            change_pass_serializer.save()
        serializer.save()
        return Response(serializer.data, 200)

    @action(detail=False, methods=["delete"])
    def delete_current(self, request):
        request.user.delete()
        return Response({"success": "User successfully deleted."}, 204)


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


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def homepage(request):
    places = GetPlaceSerializer(request.user.places.all(), many=True).data
    user_data = UserInfoSerializer(request.user).data
    return Response({**user_data, "places": places})


class PlaceViewSet(viewsets.GenericViewSet):
    queryset = Place.objects.all()

    def get_permissions(self):
        if self.action in ("get_places", "create_place"):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsSameUserOrReadonly]
        return [permission() for permission in permission_classes]

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    @action(detail=False, methods=["get"])
    def get_places(self, request):
        serializer = GetPlaceSerializer(
            self.get_queryset(), many=True, context={"user": request.user}
        )
        return Response(serializer.data, 200)

    @action(detail=False, methods=["post"])
    def create_place(self, request):
        serializer = ClientValidatePlaceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        transformed_data = convert_placedata_to_geojson(serializer.validated_data)
        inner_serializer = CreateUpdatePlaceSerializer(
            data=transformed_data, context={"user": request.user}
        )
        inner_serializer.is_valid(raise_exception=True)
        place = inner_serializer.save()

        response_serializer = GetPlaceSerializer(place, context={"user": request.user})
        return Response(response_serializer.data, 201)

    @action(detail=True, methods=["patch"], permission_classes=[IsSameUserOrReadonly])
    def update_place(self, request, pk=None):
        place = self.get_object()
        serializer = ClientValidatePlaceSerializer(
            place, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)

        transformed_data = convert_placedata_to_geojson(serializer.validated_data)
        inner_serializer = CreateUpdatePlaceSerializer(
            place, data=transformed_data, context={"user": request.user}, partial=True
        )
        inner_serializer.is_valid(raise_exception=True)
        place = inner_serializer.save()

        response_serializer = GetPlaceSerializer(place, context={"user": request.user})
        return Response(response_serializer.data, 200)

    @action(detail=True, methods=["delete"], permission_classes=[IsSameUserOrReadonly])
    def delete_place(self, request, pk=None):
        place = self.get_object()
        place.delete()
        return Response({"success": "Place successfully removed."}, 204)


class PlaceImagesViewSet(viewsets.GenericViewSet):
    queryset = Place.objects.all()
    permission_classes = (IsSameUserOrReadonly,)

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    @action(detail=True, methods=["post"])
    def add_images(self, request, pk=None):
        place = self.get_object()
        serializer = AddPlaceImagesSerializer(
            data=request.data, context={"place": place}
        )
        serializer.is_valid(raise_exception=True)
        place = serializer.create()

        response_serializer = GetPlaceSerializer(place, context={"user": request.user})
        return Response(response_serializer.data, 200)

    @action(detail=True, methods=["delete"])
    def remove_images(self, request, pk=None):
        place = self.get_object()
        serializer = RemovePlaceImagesSerializer(
            data=request.data, context={"place": place}
        )
        serializer.is_valid(raise_exception=True)
        serializer.delete()

        response_serializer = GetPlaceSerializer(place, context={"user": request.user})
        return Response(response_serializer.data, 200)
