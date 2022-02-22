from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView

from .serializers import RegisterUserSerializer

User = get_user_model()


class RegisterAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer
