from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import Client

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
    LocationSerializer,
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


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def homepage(request):
    location_serializer = LocationSerializer(data=request.data)
    location_serializer.is_valid(raise_exception=True)

    client = Client()
    user_data = client.get(
        path="/api/users/settings/",
        **{
            "HTTP_AUTHORIZATION": request.META["HTTP_AUTHORIZATION"],
        },
    ).json()

    return Response(
        {
            **user_data,
            "places": [
                {
                    "name": "Tesla Bar",
                    "title": "Tesla Bar",
                    "address": "Zybitskaya st., 6",
                    "rating": 4.12,
                    "city": "Minsk",
                    "category": "Bar",
                    "description": "Just a regular bar, nothing special.",
                    "location": {
                        "latitude": 53.90631212153169,
                        "longitude": 27.5577447932532,
                    },
                    "images": [
                        "https://routes4life-media.s3.amazonaws.com/media/mockup_places_photos/bar-secondary1.jpg",
                        "https://routes4life-media.s3.amazonaws.com/media/mockup_places_photos/bar-secondary2.jpg",
                    ],
                    "mainImage": "https://routes4life-media.s3.amazonaws.com/media/mockup_places_photos/bar-main.jpg",
                },
                {
                    "name": "Edo Japan",
                    "title": "Edo Japan",
                    "address": "1067 I-30 Frontage Rd #109, Rockwall, TX 75087, USA, Texas",
                    "rating": 3.8,
                    "city": "Mobil City",
                    "category": "Restaurant",
                    "description": "Just a regular foodcort, nothing special.",
                    "location": {
                        "latitude": 33.690417515989516,
                        "longitude": -96.42122490888232,
                    },
                    "images": [
                        "https://routes4life-media.s3.amazonaws.com/media/mockup_places_photos/foodcort-secondary1.jpg",
                        "https://routes4life-media.s3.amazonaws.com/media/mockup_places_photos/foodcort-secondary2.jpg",
                    ],
                    "mainImage": "https://routes4life-media.s3.amazonaws.com/media/mockup_places_photos/foodcort-main.png",
                },
                {
                    "name": "GYM Express",
                    "title": "GYM Express",
                    "address": "Pobediteley ave., 84",
                    "rating": 4.56,
                    "city": "Minsk",
                    "category": "Gym",
                    "description": "Just a regular gym, nothing special.",
                    "location": {
                        "latitude": 53.93817828637732,
                        "longitude": 27.48793170027158,
                    },
                    "images": [
                        "https://routes4life-media.s3.amazonaws.com/media/mockup_places_photos/gym-secondary1.jpg",
                        "https://routes4life-media.s3.amazonaws.com/media/mockup_places_photos/gym-secondary2.jpeg",
                    ],
                    "mainImage": "https://routes4life-media.s3.amazonaws.com/media/mockup_places_photos/gym-main.jpg",
                },
            ],
        }
    )


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
