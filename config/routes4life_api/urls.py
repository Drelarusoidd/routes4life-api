from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import (
    ForgotPasswordViewSet,
    RegisterAPIView,
    UserInfoViewSet,
    change_my_email,
    change_my_password,
)

urlpatterns = [
    path("auth/get-token/", TokenObtainPairView.as_view(), name="get_token_pair"),
    path("auth/signup/", RegisterAPIView.as_view(), name="register"),
    path("auth/change-email/", change_my_email, name="change_email"),
    path("auth/change-password/", change_my_password, name="change_password"),
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
                "put": "update_current",
                "patch": "partial_update_current",
            }
        ),
        name="user_settings",
    ),
]
