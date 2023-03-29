"""
Tests for the recipe APIs.
"""

from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from config.models import Recipe
from recipe.serializers import (
    RecipeModelSerializer,
    RecipeDetailModelSerializer
)


RECIPE_URL = reverse('recipe:recipe-list')


def recipe_detail_url(recipe_id):
    """Return a recipe detail url."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


def create_recipe(user, **params):
    """Create and return a smple recipe for test."""

    defaults = {
        'title': 'Sample Test Recipe Title',
        'description': 'sample test recipe description.',
        'make_time_minutes': 22,
        'price': Decimal('5.25'),
        'link': 'https://example.com/recipe.pdf'
    }
    defaults.update(**params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeAPITests(TestCase):
    """Test for unauthenticated Recipe API requests."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_recipe_list_auth_required(self):
        """Test auth is required to call API."""

        response = self.client.get(path=RECIPE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test for authenticated Recipe API Requests."""

    def setUp(self) -> None:
        self.client = APIClient()

        self.user = create_user(
            email='test@example.com',
            username='test_user',
            password='test_pass123'
        )
        self.client.force_authenticate(self.user)

    def test_recipe_list_get_success(self):
        """Test for recipe list get request."""

        create_recipe(user=self.user)
        create_recipe(user=self.user)

        response = self.client.get(path=RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeModelSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipe_list_limited_to_authenticated_user(self):
        """Test for recipe list limited to authenticated user."""

        other_user = create_user(
            email='other_test@example.com',
            username='other_test_user',
            password='test_pass123'
        )

        create_recipe(user=other_user)
        create_recipe(user=self.user)

        response = self.client.get(path=RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeModelSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipe_detail_get_success(self):
        """Test for recipe detail get request."""

        recipe = create_recipe(user=self.user)

        url = recipe_detail_url(recipe_id=recipe.id)
        response = self.client.get(path=url)

        serializer = RecipeDetailModelSerializer(recipe)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipe_post_for_create_success(self):
        """Test creating a recipe successful."""

        payload = {
            'title': 'Sample Test Recipe Title',
            'description': 'sample test recipe description.',
            'make_time_minutes': 23,
            'price': Decimal('5.35'),
            'link': 'https://example.com/recipe.pdf'
        }
        response = self.client.post(path=RECIPE_URL, data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=response.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        self.assertEqual(recipe.user, self.user)

    def test_recipe_partial_update_success(self):
        """Test partial update of a recipe successful."""

        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(
            user=self.user,
            title='Sample Test Recipe Title',
            description='sample test recipe description.',
            make_time_minutes=23,
            price=Decimal('5.35'),
            link=original_link
        )

        payload = {
            'title': 'Partial update sample Test Recipe Title',
            'description': 'partial update sample test recipe description.',
        }
        url = recipe_detail_url(recipe_id=recipe.id)
        response = self.client.patch(path=url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.description, payload['description'])

    def test_recipe_full_update_success(self):
        """Test full update of a recipe successful."""

        recipe = create_recipe(
            user=self.user,
            title='Sample Test Recipe Title',
            description='sample test recipe description.',
            make_time_minutes=23,
            price=Decimal('5.35'),
            link='https://example.com/recipe.pdf'
        )

        payload = {
            'title': 'full update sample Test Recipe Title',
            'description': 'full update sample test recipe description.',
            'make_time_minutes': 5,
            'price': Decimal('5.65'),
            'link': 'https://example.com/recipe_update.pdf'
        }
        url = recipe_detail_url(recipe_id=recipe.id)
        response = self.client.put(path=url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        self.assertEqual(recipe.user, self.user)

    def test_recipe_update_user_returns_error(self):
        """Test changing the recipe user returns an error."""

        other_user = create_user(
            email='other_test@example.com',
            username='test_other_user',
            password='test_pass123'
        )
        recipe = create_recipe(user=other_user)

        payload = {
            'user': self.user.id,
        }
        url = recipe_detail_url(recipe_id=recipe.id)
        response = self.client.patch(path=url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, other_user)

    def test_recipe_delete_success(self):
        """Test deleting a recipe successful."""

        recipe = create_recipe(user=self.user)

        url = recipe_detail_url(recipe_id=recipe.id)
        response = self.client.delete(path=url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_delete_for_other_user_return_error(self):
        """Test deleting other users recipe returns error."""

        other_user = create_user(
            email='other_test@example.com',
            username='test_other_user',
            password='test_pass123'
        )
        recipe = create_recipe(user=other_user)

        url = recipe_detail_url(recipe_id=recipe.id)
        response = self.client.delete(path=url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())