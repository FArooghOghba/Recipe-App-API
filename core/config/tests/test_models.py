"""
Tests for models.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTest(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """
        Test creating a user with an email is successful.
        :return:
        """
        email = 'test@example.com'
        username = 'test_user'
        password = 'test_pass123'
        user = get_user_model().objects.create_user(
            email=email,
            username=username,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.check_password(password), password)

    def test_new_user_email_normalized(self):
        """Test email address is normalized for new users."""

        sample_emails = (
            ['test1@EXAMPLE.com', 'test1@example.com', 'test_username1'],
            ['Test2@Example.com', 'Test2@example.com', 'test_username2'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com', 'test_username3'],
            ['test4@example.COM', 'test4@example.com', 'test_username4'],
        )
        for email, expected_format, username in sample_emails:
            user = get_user_model().objects.create_user(
                email=email, username=username, password='sample123'
            )
            self.assertEqual(user.email, expected_format)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email='', username='test_user123', password='test123'
            )

    def test_new_user_without_username_raises_error(self):
        """Test that creating a user without a username raises a ValueError."""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email='test6@example.com', username='', password='test123'
            )

    def test_create_superuser(self):
        """Test creating a superuser."""

        email = 'test7@example.com'
        username = 'test_user5'
        password = 'test_pass123'
        user = get_user_model().objects.create_superuser(
            email=email,
            username=username,
            password=password
        )

        self.assertTrue(user.is_verified)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_new_superuser_without_extra_fields_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_superuser(
                email='test8@example.com', username='test_user123',
                password='test123', is_superuser=False
            )

