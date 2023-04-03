"""
Tests for the ingredient APIs.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from config.models import Ingredient

from recipe.serializers import IngredientModelSerializer


INGREDIENT_URL = reverse('recipe:ingredient-list')


def ingredient_detail_url(ingredient_id):
    """Return an ingredient detail url."""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(
    email='test@example.com', username='test_user', password='test_pass123'
):
    """Create and return a new user."""
    return get_user_model().objects.create_user(
        email=email,
        username=username,
        password=password
    )


class PublicIngredientAPITests(TestCase):
    """Test for unauthenticated ingredient API requests."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_ingredient_list_auth_required(self):
        """Test auth is required to retrieving ingredients."""

        response = self.client.get(path=INGREDIENT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITests(TestCase):
    """Test for authenticated ingredient API requests."""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_ingredient_get_list_success(self):
        """Test for get ingredient list API request."""

        Ingredient.objects.create(user=self.user, name='ing_name')
        Ingredient.objects.create(user=self.user, name='ing_name2')

        response = self.client.get(path=INGREDIENT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientModelSerializer(ingredients, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_ingredient_list_limited_to_authenticated_user(self):
        """Test for ingredient list limited to authenticated user."""

        other_user = create_user(
            email='other_test@example.com',
            username='other_test_user',
        )

        Ingredient.objects.create(user=other_user, name='ing_test_name')
        Ingredient.objects.create(user=self.user, name='ing_test_name2')
        ingredient = Ingredient.objects.create(
            user=self.user, name='ing_test_name3'
        )

        response = self.client.get(path=INGREDIENT_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ingredients = Ingredient.objects.filter(
            user=self.user
        ).order_by('-name')
        serializer = IngredientModelSerializer(ingredients, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], ingredient.name)
        self.assertEqual(response.data[0]['id'], ingredient.id)

    def test_ingredient_patch_for_update_success(self):
        """Test update of a ingredient is successful."""

        ingredient = Ingredient.objects.create(
            user=self.user, name='ingredient_test_name'
        )

        payload = {'name': 'ingredient_test_name_edited'}
        url = ingredient_detail_url(ingredient_id=ingredient.id)
        response = self.client.patch(path=url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])
        self.assertEqual(ingredient.user, self.user)

    def test_ingredient_delete_success(self):
        """Test deleting a ingredient successful."""

        ingredient = Ingredient.objects.create(
            user=self.user, name='ingredient_test_name'
        )
        url = ingredient_detail_url(ingredient_id=ingredient.id)
        response = self.client.delete(path=url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=ingredient.id).exists())
