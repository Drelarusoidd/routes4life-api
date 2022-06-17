from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from routes4life_api.views import (
    ForgotPasswordViewSet,
    NearestPlacesAPIView,
    PlaceViewSet,
    RegisterAPIView,
    SearchPlacesAPIView,
    UpdatePlaceSecondaryImagesAPIView,
    UserInfoViewSet,
    change_my_email,
    homepage,
)

urlpatterns = [
    path("auth/get-token/", TokenObtainPairView.as_view(), name="get_token_pair"),
    path("auth/signup/", RegisterAPIView.as_view(), name="register"),
    path("auth/change-email/", change_my_email, name="change_email"),
    path(
        "auth/reset-password/",
        ForgotPasswordViewSet.as_view(
            {
                "get": "send_email",
                "post": "send_reset_code",
                "patch": "change_password",
            }
        ),
        name="reset-password",
    ),
    path(
        "users/settings/",
        UserInfoViewSet.as_view(
            {
                "get": "get_current",
                "patch": "partial_update_current",
                "delete": "delete_current",
            }
        ),
        name="user_settings",
    ),
    path("homepage/", homepage, name="homepage"),
    path(
        "places/",
        PlaceViewSet.as_view(
            {
                "get": "get_places",
                "post": "create_place",
            }
        ),
        name="places_list_create",
    ),
    path(
        "places/<int:pk>/",
        PlaceViewSet.as_view(
            {
                "patch": "update_place",
                "delete": "delete_place",
            }
        ),
        name="places_update_delete",
    ),
    path(
        "places/<int:pk>/images/",
        UpdatePlaceSecondaryImagesAPIView.as_view(),
        name="place_images",
    ),
    path(
        "places/nearest/",
        NearestPlacesAPIView.as_view(),
        name="nearest_places",
    ),
    path("places/search/", SearchPlacesAPIView.as_view(), name="search_places"),
]
