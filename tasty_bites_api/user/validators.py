from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

User = get_user_model()

MINIMUM_PASSWORD_LENGTH = 8
MINIMUM_USERNAME_LENGTH = 3


def user_creation_validator(username: str, email: str, password: str, confirm_password) -> bool:
    """Validate the user data before saving it to the database."""
    try:
        validate_email(email)
    except ValidationError:
        raise ValidationError('Invalid email address.')

    username_validator(username)

    user_password_validator(password, confirm_password)

    if User.objects.filter(email=email):
        raise ValueError('Email already exists.')
    return True


def user_password_validator(password: str, confirm_password: str = "") -> bool:
    """Validate the user password before saving it to the database."""
    if len(password) < MINIMUM_PASSWORD_LENGTH:
        raise ValidationError(f'Password must be at least {MINIMUM_PASSWORD_LENGTH} characters long.')
    if password != confirm_password:
        raise ValidationError('Passwords do not match.')
    return True


def user_update_validator(username: str, password: str, confirm_password: str) -> bool:
    """Validate the user data before updating it in the database."""
    username_validator(username)
    user_password_validator(password, confirm_password)
    return True


def username_validator(username: str) -> bool:
    """Validate the username before saving it to the database."""
    if len(username) < MINIMUM_USERNAME_LENGTH:
        raise ValidationError(f'Username must be at least {MINIMUM_USERNAME_LENGTH} characters long.')
    if User.objects.filter(username=username).exists():
        raise ValueError('Username already exists.')
    return True
