from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView  # , TokenRefreshView

from .views import RegisterAPIView

urlpatterns = [
    path("auth/get-token/", TokenObtainPairView.as_view(), name="get_token_pair"),
    # path("auth/token/refresh/", TokenRefreshView().as_view(), name="token_refresh"),
    path("auth/signup/", RegisterAPIView.as_view(), name="register"),
]
