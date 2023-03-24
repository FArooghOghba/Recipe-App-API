"""
Tests for the user API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
CREATE_ATH_TOKEN_URL = reverse('user:token')
USER_PROFILE_URL = reverse('user:profile')


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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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

    def test_create_token_success(self):
        """Test generate token for valid credentials."""

        user_detail = {
            'email': 'test@example.com',
            'username': 'test_user',
            'password': 'test_pass123'
        }
        create_user(**user_detail)
        user = get_user_model().objects.get(email=user_detail['email'])
        user.is_verified = True
        user.save()

        payload = {
            'email': user_detail['email'],
            'password': user_detail['password'],
        }
        response = self.client.post(path=CREATE_ATH_TOKEN_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_create_token_wrong_pass(self):
        """Test returns error if password is wrong."""

        user_detail = {
            'email': 'test@example.com',
            'username': 'test_user',
            'password': 'test_pass123'
        }
        create_user(**user_detail)

        payload = {
            'email': user_detail['email'],
            'password': 'wrong_pass',
        }
        response = self.client.post(path=CREATE_ATH_TOKEN_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_create_token_blank_pass(self):
        """Test returns error if password is blank."""

        user_detail = {
            'email': 'test@example.com',
            'username': 'test_user',
            'password': 'test_pass123'
        }
        create_user(**user_detail)

        payload = {
            'email': user_detail['email'],
            'password': '',
        }
        response = self.client.post(path=CREATE_ATH_TOKEN_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_create_token_for_unverified_user(self):
        """Test returns error if password is blank."""

        user_detail = {
            'email': 'test@example.com',
            'username': 'test_user',
            'password': 'test_pass123'
        }
        create_user(**user_detail)

        payload = {
            'email': user_detail['email'],
            'password': '',
        }
        response = self.client.post(path=CREATE_ATH_TOKEN_URL, data=payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_retrieve_profile_for_unauthorized_user(self):
        """Test authentication is required for users to check their profile."""

        response = self.client.get(path=USER_PROFILE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    """Test user API requests that require authentication."""

    def setUp(self) -> None:
        self.client = APIClient()

        self.user = create_user(
            email='test@example.com',
            username='test_user',
            password='test_pass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_for_authorized_user(self):
        """Test retrieving profile for authenticated user."""

        response = self.client.get(path=USER_PROFILE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                'email': self.user.email,
                'username': self.user.username
            }
        )

    def test_post_method_not_allowed_for_profile(self):
        """Test POST method not allowed for profile endpoint."""

        response = self.client.post(path=USER_PROFILE_URL, data={})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile_success(self):
        """Test updating the user profile for the authenticated user."""

        payload = {
            'username': 'new_user_name',
            'password': 'new_password123'
        }
        response = self.client.patch(path=USER_PROFILE_URL, data=payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, payload['username'])
        self.assertTrue(self.user.check_password(payload['password']))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
