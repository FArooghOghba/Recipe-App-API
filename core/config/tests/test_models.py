"""
Tests for models.
"""

from unittest.mock import patch
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from config import models


def create_user():
    """Create and return a user."""

    return get_user_model().objects.create_user(
        email='test@example.com',
        username='test_user',
        password='test_pass123'
    )


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

    def test_create_recipe_successful(self):
        """Test create a recipe is successful."""

        user = create_user()

        recipe = models.Recipe.objects.create(
            user=user,
            title='Recipe Test Title',
            description='Recipe smple test description',
            make_time_minutes=5,
            price=Decimal(5.50)
        )

        self.assertEqual(recipe.title, str(recipe))

    def test_tag_create_success(self):
        """Test creating a tag is successful."""

        user = create_user()
        tag = models.Tag.objects.create(user=user, name='test_tag')

        self.assertEqual(tag.name, str(tag))

    def test_ingredient_create_successful(self):
        """Test creating ingredient is successful."""

        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name='test_ingredient_name'
        )

        self.assertEqual(ingredient.name, str(ingredient))

    @patch('config.models.uuid.uuid4')
    def test_recipe_create_file_name_uuid_for_image_path(self, mock_uuid):
        """Test generating image path for recipe object."""

        uuid = 'test_uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')
