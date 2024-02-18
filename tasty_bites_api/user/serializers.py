import os

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import Token
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, AuthUser

from .validators import user_creation_validator, user_update_validator
from .models import UserAvatar

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer that handles converting user data during registration. Also handles validation of data."""
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)

    class Meta:
        """Metaclass to define the model and fields to be serialized."""
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def create(self, validated_data):
        """Override standard create method to create a user with the validated data."""
        user: User = User

        cleaned_data: dict = self.validated_data

        username: str = cleaned_data.get('username')
        email: str = cleaned_data.get('email')
        password: str = cleaned_data.get('password')
        confirmation_password: str = cleaned_data.get('confirmation_password')

        user_creation_validator(username, email, password, confirmation_password)

        user = User.objects.create(
            username=username,
            email=email,
        )

        user.set_password(password)
        user.save()

        return user


class UserLoginSerializer(TokenObtainPairSerializer):
    """Serializer that handles converting and validation of user data during login."""
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def get_token(self, user: User) -> Token:
        """Override the get_token method to include the username in the token."""
        token: Token = super().get_token(user)
        token['username']: str = user.username
        return token

    class Meta:
        """Metaclass to define the model and fields to be serialized."""
        model = User
        fields = ['username', 'password']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer that converts user profile data into JSON."""
    username = serializers.ReadOnlyField()
    avatar = serializers.ImageField(source='useravatar.avatar', required=False)

    class Meta:
        """Metaclass to define the model and fields to be serialized."""
        model = User
        fields = ['username', 'avatar']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer that handles converting and validation of user data during update."""
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    confirmation_password = serializers.CharField(required=False)
    avatar = serializers.ImageField(source='useravatar.avatar', required=False)

    class Meta:
        """Metaclass to define the model and fields to be serialized."""
        model = User
        fields = ['username', 'password', 'confirmation_password', 'avatar']

    def save(self, **kwargs):
        """Override the save method to update the user with the validated data and cleaned up old avatar."""
        user: User = self.instance
        cleaned_data: dict = self.validated_data
        username: str = cleaned_data.get('username')
        password: str = cleaned_data.get('password')
        confirmation_password: str = cleaned_data.get('confirmation_password')

        user_update_validator(username, password, confirmation_password)

        new_avatar: UserAvatar.avatar = cleaned_data.get('avatar')
        if new_avatar:
            old_avatar_instance: UserAvatar.avatar = user.useravatar

            if old_avatar_instance:
                old_avatar_instance.delete()
                old_avatar_path: str = os.path.join(settings.MEDIA_ROOT, str(old_avatar_instance.avatar))
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)

            user_avatar_instance = UserAvatar(user=user, avatar=new_avatar)
            user_avatar_instance.save()

        user.username = username
        user.set_password(password)
        user.save()
        return user
