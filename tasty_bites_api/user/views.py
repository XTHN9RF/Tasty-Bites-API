from django.urls import reverse
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import action
from .models import User
from .serializers import UserRegistrationSerializer
from .serializers import UserLoginSerializer
from .serializers import UserProfileSerializer
from .permissions import IsObjectOwnerOrReadOnly

from common.utils import HttpMethods

from user.tasks import send_email_task


class UserLoginView(TokenObtainPairView):
    """A view that allows user to login into website and get both access and refresh tokens."""
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer


class UserRegistrationView(generics.CreateAPIView, ViewSet):
    """A view that allows user to register into website, providing username, email and password."""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)

    @action(detail=False, methods=HttpMethods.POST.value)
    def create_user(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.create(serializer.validated_data)

            token = RefreshToken.for_user(user)

            relative_link = reverse('user:activate_user', kwargs={'token': str(token)})

            current_link = request.scheme + '://' + request.get_host()

            mail_subject = 'Account Activation'
            mail_message = (f'Please click the following link to activate your account:\n' +
                            f'{current_link}{relative_link}')

            send_email_task.delay(user.username, mail_subject, mail_message)

            return Response(
                {'message': 'User created successfully. Check your email for account activation.'}, status=201)

        return Response(serializer.errors, status=400)


class UserActivationView(ViewSet):
    """A view that allows user to activate their account by clicking on the link sent to their email."""
    permission_classes = (AllowAny,)

    @action(detail=True, methods=HttpMethods.GET.value)
    def activate_user(self, request, token):
        try:
            token = RefreshToken(token)
            user = User.objects.get(id=token.payload['user_id'])
            user.is_active = True
            user.save()
            return Response({'message': 'User activated successfully.'}, status=200)
        except TokenError:
            return Response({'message': 'Invalid or expired token'}, status=400)
        except User.DoesNotExist:
            return Response({'message': 'User does not exist'}, status=400)


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
        user = User.objects.get(username=self.request.user.username)
        new_password = User.objects.make_random_password()
        user.set_password(new_password)
        user.save()

        mail_subject = 'Password Reset'
        mail_message = f'Your new password is: {new_password}'

        send_email_task.delay(user.username, mail_subject, mail_message)

        return Response({'message': 'Password reset successfully. Check your email for new password.'}, status=200)
