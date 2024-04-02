from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action
import os
from dotenv import load_dotenv
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
    permission_classes = (IsAuthenticated, IsObjectOwnerOrReadOnly,)
    serializer_class = UserProfileSerializer

    @action(detail=False, methods=HttpMethods.PUT.value)
    def update_profile(self, request):
        user = request.user
        serializer = self.serializer_class(user, data=request.data, partial=True)
        cleaned_data = serializer.validate(request.data)
        avatar = cleaned_data.get('avatar', None)
        if serializer.is_valid():
            serializer.update(user, cleaned_data)
            user.set_password(cleaned_data.get('password'))
            user.useravatar.avatar = avatar
            user.useravatar.save()
            user.save()
            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=400)


class UserPasswordResetView(ViewSet):
    """A view that allows user to resend password reset email."""
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=HttpMethods.POST.value)
    def reset_password(self, request):
        load_dotenv()
        user = User.objects.get(username=self.request.user.username)
        new_password = User.objects.make_random_password()
        user.set_password(new_password)
        user.save()

        send_mail(
            'Password Reset',
            f'Your new password is: {new_password}',
            os.getenv('EMAIL_HOST_USER'),
            [user.email],
            fail_silently=False
        )

        return Response({'message': 'Password reset successfully. Check your email for new password.'}, status=200)
