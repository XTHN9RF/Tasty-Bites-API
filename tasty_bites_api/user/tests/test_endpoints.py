from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import UserAvatar

from common.constants import DEFAULT_USER_AVATAR


class PublicUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpassword',
            is_active=True,
        )
        self.avatar = UserAvatar.objects.create(user=self.user, avatar=DEFAULT_USER_AVATAR)

    def test_create_user(self):
        url = reverse('user:register')
        data = {
            'username': 'testuser2',
            'email': 'test2@test.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(username=data['username'])
        self.assertTrue(user.check_password(data['password1']))
        self.assertTrue(user.check_password(data['password2']))
        self.assertEqual(user.email, data['email'])
        self.assertEqual(user.username, data['username'])
        self.assertEqual(user.useravatar.avatar, DEFAULT_USER_AVATAR)
        self.assertEqual('User created successfully. Check your email for account activation.',
                         response.data['message'])

    def test_login_user(self):
        url = reverse('user:login')
        data = {
            'username': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        self.assertFalse('username' in response.data)
        self.assertFalse('email' in response.data)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer')

    def test_random_user_profile(self):
        url = reverse('user:user_profile', kwargs={'username': self.user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_own_user_profile(self):
        url = reverse('user:your_profile')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_profile(self):
        url = reverse('user:update_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser', email='test@test.com', password='testpassword', )
        self.client.force_authenticate(user=self.user)
        self.user_avatar = UserAvatar.objects.create(user=self.user, avatar=DEFAULT_USER_AVATAR)

    def test_random_user_profile(self):
        random_user = get_user_model().objects.create_user(username='randomuser', email='random@test.com',
                                                           password='randompassword')
        rand_avatar = UserAvatar.objects.create(user=random_user, avatar=DEFAULT_USER_AVATAR)
        url = reverse('user:user_profile', kwargs={'username': random_user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], random_user.username)
        self.assertEqual(response.data['avatar'], rand_avatar.avatar.url)

    def test_own_user_profile(self):
        url = reverse('user:your_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['avatar'], self.user_avatar.avatar.url)

    def test_update_user_profile(self):
        url = reverse('user:update_profile')
        data = {
            'username': 'newusername',
            'password': 'newpassword',
            'confirm_password': 'newpassword',
            'avatar': '/media/user_avatars/1694521009786.jpg',
        }

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, data['username'])
        self.assertTrue(self.user.check_password(data['password']))
        self.assertEqual(self.user.useravatar.avatar.url, "/media" + data['avatar'])

    def test_reset_password(self):
        old_password = self.user.password
        url = reverse('user:reset_password')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertNotEqual(old_password, self.user.password)
        self.assertEqual(response.data['message'], 'Password reset successfully. Check your email for new password.')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
