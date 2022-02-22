from django.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView  # , TokenRefreshView

from .views import RegisterAPIView, UserInfoViewSet, change_my_email

router = SimpleRouter()
router.register(r"users", UserInfoViewSet)

urlpatterns = [
    path("auth/get-token/", TokenObtainPairView.as_view(), name="get_token_pair"),
    # path("auth/token/refresh/", TokenRefreshView().as_view(), name="token_refresh"),
    path("auth/signup/", RegisterAPIView.as_view(), name="register"),
    path("auth/change-email/", change_my_email, name="change_email"),
]

urlpatterns += router.urls
