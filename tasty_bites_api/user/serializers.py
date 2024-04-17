import os

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, AuthUser

from .validators import user_creation_validator, user_update_validator
from .models import UserAvatar

from common.constants import DEFAULT_USER_AVATAR_PATH

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
        password: str = cleaned_data.get('password1')
        confirmation_password: str = cleaned_data.get('password2')

        user_creation_validator(username, email, password, confirmation_password)

        user = User.objects.create(
            username=username,
            email=email,
        )

        UserAvatar.objects.create(user=user, avatar=DEFAULT_USER_AVATAR_PATH)

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
    avatar = serializers.CharField(source='useravatar.avatar.url', read_only=True)

    class Meta:
        """Metaclass to define the model and fields to be serialized."""
        model = User
        fields = ['username', 'avatar']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer that handles converting and validation of user data during update."""
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    confirmation_password = serializers.CharField(required=False)
    avatar = serializers.CharField(source='user.useravatar.avatar.url', required=False)

    class Meta:
        """Metaclass to define the model and fields to be serialized."""
        model = User
        fields = ['username', 'password', 'confirmation_password', 'avatar']

    def validate(self, data):
        """Override the validate method to validate the user data."""
        username = data.get('username')
        password = data.get('password')
        confirmation_password = data.get('confirmation_password')

        user_update_validator(username, password, confirmation_password)

        return data

    def update(self, instance, validated_data):
        """Override the update method to update the user with the validated data."""
        username = validated_data.get('username', instance.username)
        password = validated_data.get('password', instance.password)
        confirmation_password = validated_data.get('confirmation_password', instance.password)

        if 'avatar' in validated_data:
            new_avatar = validated_data.get('avatar')
            old_avatar_instance = instance.useravatar
            old_avatar_path = old_avatar_instance.avatar.url
            if old_avatar_path not in DEFAULT_USER_AVATAR_PATH:
                os.remove(old_avatar_path)
            instance.useravatar.avatar = new_avatar

        instance.username = username
        instance.set_password(password)

        instance.save()
        return instance
