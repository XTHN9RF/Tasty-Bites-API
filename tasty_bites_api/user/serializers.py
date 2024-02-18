from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import Token

from .validators import user_creation_validator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, AuthUser

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
        user = User

        cleaned_data = self.validated_data

        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        confirmation_password = cleaned_data.get('confirmation_password')

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
        token = super().get_token(user)
        token['username'] = user.username
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
