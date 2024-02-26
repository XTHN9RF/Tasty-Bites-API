from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action

from .models import User
from .serializers import UserRegistrationSerializer
from .serializers import UserLoginSerializer
from .serializers import UserProfileSerializer
from .permissions import IsObjectOwnerOrReadOnly

from common.utils import HttpMethods


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


class UserUpdateView(ViewSet):
    """A view that allows user to update their profile."""
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    @action(detail=False, methods=HttpMethods.PUT.value)
    def update_profile(self, request):
        user = request.user
        serializer = self.serializer_class(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.update(user, request.data)
            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=400)
