from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def user_creation_validator(self, username: str, email: str, password: str, confirm_password) -> bool:
    """Validate the user data before saving it to the database."""
    try:
        validate_email(email)
    except ValidationError:
        raise ValidationError('Invalid email address.')

    username_validator(self, username)

    user_password_validator(self, password, confirm_password)

    if self.filter(email=email):
        raise ValueError('Email already exists.')
    return True


def user_password_validator(self, password: str, confirm_password: str = "") -> bool:
    """Validate the user password before saving it to the database."""
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    if password != confirm_password:
        raise ValidationError('Passwords do not match.')
    return True


def user_login_validator(self, email: str, password: str) -> bool:
    """Validate the user login data before authenticating the user."""
    password = make_password(password)
    if not self.filter(email=email) or not self.filter(password=password):
        raise ValidationError('Invalid email or password.')
    return True


def user_update_validator(self, username: str, password: str, confirm_password: str) -> bool:
    """Validate the user data before updating it in the database."""
    if len(username) < 3:
        raise ValidationError('Username must be at least 3 characters long.')

    if self.filter(username=username):
        raise ValueError('Username already exists.')

    user_password_validator(self, password, confirm_password)
    return True


def username_validator(self, username: str) -> bool:
    """Validate the username before saving it to the database."""
    if len(username) < 3:
        raise ValidationError('Username must be at least 3 characters long.')
    if self.filter(username=username):
        raise ValueError('Username already exists.')
    return True
