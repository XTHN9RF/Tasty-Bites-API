from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager


class UserModelManager(BaseUserManager):
    """Model manager class that handles overwriting of user creation methods"""

    def create_user(self, username, email, password, **extra_fields):
        """Create and save a standard User with the given username, email, and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        """Create and save a superuser with the given username, email, and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model that extends the AbstractUser class"""
    email = models.EmailField(max_length=60, unique=True)
    username = models.CharField(max_length=30, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserModelManager()

    class Meta:
        """Metaclass for the User model which used to define custom verbose name and ordering of the model"""
        verbose_name = 'User'
        ordering = ['-created_at']

    def __str__(self):
        """String representation of the User model"""
        return self.username


class UserAvatar(models.Model):
    """Model class that extends the User model to store user avatars"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='user_avatars/',
                               default='user_avatars/default_avatar.png')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Metaclass for the UserAvatar model which used to define custom verbose name and ordering of the model"""
        verbose_name = 'User Avatar'
        ordering = ['-created_at']

    def __str__(self):
        """String representation of the UserAvatar model"""
        return self.user.username
