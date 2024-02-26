from django.test import TestCase

from user.validators import *


class TestUserValidators(TestCase):
    def test_user_creation_validator(self):
        self.assertTrue(user_creation_validator('test', 'test@test.com', 'testpassword', 'testpassword'))
        with self.assertRaises(ValidationError):
            user_creation_validator('test', 'testtest.com', 'testpassword', 'testpassword')

    def test_user_password_validator(self):
        self.assertTrue(user_password_validator('testpassword', 'testpassword'))
        with self.assertRaises(ValidationError):
            user_password_validator('test', 'testpassword')
        with self.assertRaises(ValidationError):
            user_password_validator('testpassword', 'testpassword1')

    def test_user_update_validator(self):
        self.assertTrue(user_update_validator('test', 'testpassword', 'testpassword'))
        with self.assertRaises(ValidationError):
            user_update_validator('test', 'test', 'testpassword')
        with self.assertRaises(ValidationError):
            user_update_validator('test', 'testpassword', 'testpassword1')
        with self.assertRaises(ValidationError):
            user_update_validator('t', 'testpassword', 'testpassword')

    def test_username_validator(self):
        self.assertTrue(username_validator('test'))
        with self.assertRaises(ValidationError):
            username_validator('t')