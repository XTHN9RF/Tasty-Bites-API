from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

User = get_user_model()


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
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    if password != confirm_password:
        raise ValidationError('Passwords do not match.')
    return True


def user_update_validator(username: str, password: str, confirm_password: str) -> bool:
    """Validate the user data before updating it in the database."""
    if len(username) < 3:
        raise ValidationError('Username must be at least 3 characters long.')

    if User.objects.filter(username=username).exists():
        raise ValueError('Username already exists.')

    user_password_validator(password, confirm_password)
    return True


def username_validator(username: str) -> bool:
    """Validate the username before saving it to the database."""
    if len(username) < 3:
        raise ValidationError('Username must be at least 3 characters long.')
    if User.objects.filter(username=username).exists():
        raise ValueError('Username already exists.')
    return True
