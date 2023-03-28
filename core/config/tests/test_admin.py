"""
Tests for the Django admin modifications.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

from config.models import Recipe

from decimal import Decimal


class AdminSiteTest(TestCase):
    """Tests for Django site admin."""

    def setUp(self) -> None:
        """Create user and client."""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            username='AdminTest',
            password='test_pass123'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='user@example.com',
            username='UserTest',
            password='test_pass123'
        )

        defaults = {
            'title': 'Sample Test Recipe Title',
            'description': 'sample test recipe description.',
            'make_time_minutes': 22,
            'price': Decimal('5.25'),
            'link': 'https://example.com/recipe.pdf'
        }
        self.recipe = Recipe.objects.create(user=self.user, **defaults)

    def test_users_list(self):
        """Test that users are listed on page."""

        url = reverse('admin:config_user_changelist')
        response = self.client.get(url)

        self.assertContains(response, self.user.username)
        self.assertContains(response, self.user.email)

    def test_edit_user_page(self):
        """Test the edit user page works."""

        url = reverse('admin:config_user_change', args=[self.user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_create_user_page(self):
        """Test the create user page works."""

        url = reverse('admin:config_user_add')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_recipes_list(self):
        """Test that recipes are listed on page."""

        url = reverse('admin:config_recipe_changelist')
        response = self.client.get(url)

        self.assertContains(response, self.recipe.user)
        self.assertContains(response, self.recipe.title)
        self.assertContains(response, self.recipe.make_time_minutes)
        self.assertContains(response, self.recipe.price)
