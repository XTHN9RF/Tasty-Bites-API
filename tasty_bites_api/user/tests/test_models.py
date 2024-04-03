from django.test import TestCase
from django.contrib.auth import get_user_model

from user.models import UserAvatar

from common.constants import DEFAULT_USER_AVATAR
from common.constants import AVATARS_UPLOAD_FOLDER


class UserAvatarModelTest(TestCase):
    """Test module for UserAvatar model"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser', password='testpassword', email='test@test.com')
        self.user_avatar = UserAvatar.objects.create(user=self.user, avatar=DEFAULT_USER_AVATAR)

    def test_user_avatar(self):
        user_avatar = UserAvatar.objects.get(user=self.user)
        self.assertEqual(user_avatar.user, self.user)
        self.assertEqual(user_avatar.avatar, DEFAULT_USER_AVATAR)

    def test_user_avatar_str(self):
        user_avatar = UserAvatar.objects.get(user=self.user)
        self.assertEqual(str(user_avatar), self.user.username)

    def test_user_avatar_verbose_name(self):
        user_avatar = UserAvatar.objects.get(user=self.user)
        self.assertEqual(user_avatar._meta.verbose_name, 'User Avatar')

    def test_avatar_upload_folder(self):
        user_avatar = UserAvatar.objects.get(user=self.user)
        self.assertEqual(user_avatar.avatar.field.upload_to, AVATARS_UPLOAD_FOLDER)


class UserModelTest(TestCase):
    """Test module for User model"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser', password='testpassword', email='test@test.com')
        self.user_avatar = UserAvatar.objects.create(user=self.user, avatar=DEFAULT_USER_AVATAR)

    def test_user(self):
        user = get_user_model().objects.get(username='testuser')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@test.com')
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_user_password(self):
        user = get_user_model().objects.get(username='testuser')
        self.assertTrue(user.check_password('testpassword'))
        self.assertFalse(user.check_password('wrongpassword'))
        self.assertFalse(user.password == 'testpassword')

    def test_email_normalization(self):
        test_emails = {
            'TEST1@TEST.COM': 'TEST1@test.com',
            'test2@TEST.com': 'test2@test.com',
            'test3@test.COM': 'test3@test.com',
        }

        for email, normalized_email in test_emails.items():
            user = get_user_model().objects.create_user(
                username='tester', password='testpassword', email=email)
            self.assertEqual(user.email, normalized_email)
            user = get_user_model().objects.get(username='tester').delete()

    def test_user_str(self):
        user = get_user_model().objects.get(username='testuser')
        self.assertEqual(str(user), 'testuser')

    def test_user_verbose_name(self):
        user = get_user_model().objects.get(username='testuser')
        self.assertEqual(user._meta.verbose_name, 'User')

    def test_user_ordering(self):
        user = get_user_model().objects.get(username='testuser')
        self.assertEqual(user._meta.ordering, ['-created_at'])
