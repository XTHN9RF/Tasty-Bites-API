from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.base_user import (AbstractBaseUser,
                                           BaseUserManager)
from .validators import (user_creation_validator,
                         user_update_validator)


class UserModelManager(BaseUserManager):
    """Custom User Manager to handle the user creation and authentication."""

    def create(self, username: str, email: str, password: str, confirm_password: str) -> 'User':
        """Overwrite the user creation method with hashing password before saving user to the database."""
        email: str = self.normalize_email(email)

        user_creation_validator(self, username, email, password, confirm_password)

        password: str = make_password(password)

        user: 'User' = self.model(
            username=username,
            email=email,
            password=password
        )
        user.save()
        return user

    def create_superuser(self, username: str, email: str, password: str, confirm_password: str) -> 'User':
        """Overwrite the create_superuser method with hashing password before saving user to the database."""
        email: str = self.normalize_email(email)

        user_creation_validator(self, username, email, password, confirm_password)

        password: str = make_password(password)

        user: 'User' = self.model(
            username=username,
            email=email,
            password=password,
            is_staff=True,
        )
        user.save()
        return user

    def update(self, **kwargs: dict) -> 'User':
        """Overwrite the user update method with hashing password before saving user to the database."""
        user_update_validator(self, kwargs)

        kwargs['password']: str = make_password(kwargs['password'])

        user: 'User' = self.model(
            username=kwargs['username'],
            password=kwargs['password']
        )
        user.save()
        return user

    def delete_by_email(self, email: str) -> 'User':
        """Overwrite the user delete method"""
        user: 'User' = self.get(email=email)
        user.delete()
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_stuff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    REQUIRED_FIELDS = ['username', 'email', 'password']

    objects = UserModelManager()

    def __str__(self):
        return self.email


class UserAvatar(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='user_avatars/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)