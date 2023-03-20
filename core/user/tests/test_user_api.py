"""
Tests for the user API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    """Test the public features of the user API."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful."""

        payload = {
            'email': 'test@example.com',
            'username': 'test_user',
            'password': 'test-pass123',
        }
        response = self.client.post(path=CREATE_USER_URL, data=payload)
        self.assertTrue(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertIsNot('password', response.data)

    def test_user_with_email_exist_error(self):
        """Test error returned if user with email exists."""

        payload = {
            'email': 'test@example.com',
            'username': 'test_user',
            'password': 'test-pass123',
        }
        create_user(**payload)
        response = self.client.post(path=CREATE_USER_URL, data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_with_username_exist_error(self):
        """Test error returned if user with username exists."""

        payload = {
            'email': 'test@example.com',
            'username': 'test_user',
            'password': 'test-pass123',
        }
        create_user(**payload)
        response = self.client.post(path=CREATE_USER_URL, data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password is less than 5 chars."""

        payload = {
            'email': 'test@example.com',
            'username': 'test_user',
            'password': 'te',
        }
        response = self.client.post(path=CREATE_USER_URL, data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
