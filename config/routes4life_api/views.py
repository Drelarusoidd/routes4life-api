from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .permissions import IsSameUserOrReadonly
from .serializers import (
    RegisterUserSerializer,
    UpdateEmailSerializer,
    UserInfoSerializer,
)

User = get_user_model()


class RegisterAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer


@api_view(["PATCH"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def change_my_email(request):
    new_email = request.data.get("email")
    serializer = UpdateEmailSerializer(request.user, {"email": new_email}, partial=True)
    # breakpoint()
    if serializer.is_valid():
        serializer.save()
        return Response({"detail": "Successfully changed email."}, 200)
    return Response({"error": "Someone has this email already."}, 400)


class UserInfoViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    serializer_class = UserInfoSerializer
    permission_classes = (IsSameUserOrReadonly,)
