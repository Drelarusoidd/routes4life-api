from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import RegisterAPIView, UserInfoViewSet, change_my_email

# router = SimpleRouter()
# router.register(r"users/settings/", UserInfoViewSet)

urlpatterns = [
    path("auth/get-token/", TokenObtainPairView.as_view(), name="get_token_pair"),
    path("auth/signup/", RegisterAPIView.as_view(), name="register"),
    path("auth/change-email/", change_my_email, name="change_email"),
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
