from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.conf import settings

from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email

from .validators import user_creation_validator

UserModel = settings.AUTH_USER_MODEL


class UserRegistrationSerializer(RegisterSerializer):
    username = serializers.CharField(required=True, max_length=100)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    confirmation_password = serializers.CharField(write_only=True)

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password': self.validated_data.get('password', ''),
            'confirmation_password': self.validated_data.get('confirmation_password', ''),
            'email': self.validated_data.get('email', ''),
        }

    def save(self, request):
        adapter: 'adapter' = get_adapter()
        user: 'UserModel' = adapter.new_user(request)
        cleaned_data: dict = self.get_cleaned_data()

        user_creation_validator(self, cleaned_data['email'], cleaned_data['username'], cleaned_data['password'],
                                cleaned_data['confirmation_password'])

        password: str = cleaned_data['password']

        adapter.save_user(request, user, self)
        user.save()

        setup_user_email(request, user, [])
        user.email = cleaned_data['email']
        user.username = cleaned_data['username']
        user.password = (make_password(password))

        return user
