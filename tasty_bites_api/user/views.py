from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import UserRegistrationSerializer
from .serializers import UserLoginSerializer
from .serializers import UserProfileSerializer


class UserLoginView(TokenObtainPairView):
    """A view that allows user to login into website and get both access and refresh tokens."""
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer


class UserRegistrationView(generics.CreateAPIView):
    """A view that allows user to register into website, providing username, email and password."""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)


class UserProfileView(generics.RetrieveAPIView):
    """A view that allows user to view their profile or other user's profile by adding username to the URL."""
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        requested_user = self.kwargs.get('username', None)

        if requested_user is None:
            return self.request.user

        return User.objects.get(username=requested_user)
