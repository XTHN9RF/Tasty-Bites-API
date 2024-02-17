from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import Token

from .validators import user_creation_validator
from .validators import user_login_validator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, AuthUser

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(required=True, write_only=True)
    password2 = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password': self.validated_data.get('password1', ''),
            'confirmation_password': self.validated_data.get('password2', ''),
            'email': self.validated_data.get('email', ''),
        }

    def create(self, validated_data):
        user = User

        cleaned_data = self.get_cleaned_data()

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
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def get_token(self, user: User) -> Token:
        token = super().get_token(user)
        token['username'] = user.username
        return token

    class Meta:
        model = User
        fields = ['username', 'password']
