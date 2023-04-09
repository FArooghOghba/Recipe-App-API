"""
Tests for the recipe APIs.
"""

from PIL import Image

from decimal import Decimal
import tempfile
import os

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from config.models import Recipe, Tag, Ingredient
from recipe.serializers import (
    RecipeModelSerializer,
    RecipeDetailModelSerializer
)


RECIPE_URL = reverse('recipe:recipe-list')


def recipe_detail_url(recipe_id):
    """Return a recipe detail url."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def image_upload_url(recipe_id):
    """Return an image upload url for recipe."""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


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

    def test_recipe_post_for_create_with_new_tags_successful(self):
        """
        Test creating recipe with nested serializer new tags is successful.
        :return:
        """

        payload = {
            'title': 'Sample Test Recipe Title',
            'description': 'sample test recipe description.',
            'make_time_minutes': 22,
            'price': Decimal('5.25'),
            'tag': [
                {'name': 'tag_test_name1'},
                {'name': 'tag_test_name2'},
            ],
            'link': 'https://example.com/recipe.pdf'
        }
        response = self.client.post(
            path=RECIPE_URL, data=payload, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.tag.count(), 2)

        for tag in payload['tag']:
            tag_exists = recipe.tag.filter(
                user=self.user,
                name=tag['name']
            ).exists()
            self.assertTrue(tag_exists)

    def test_recipe_post_for_create_with_existing_tags_successful(self):
        """
        Test creating recipe with nested serializer existing tags
         is successful.
        :return:
        """

        tag = Tag.objects.create(user=self.user, name='tag_test_name1')
        payload = {
            'title': 'Sample Test Recipe Title',
            'description': 'sample test recipe description.',
            'make_time_minutes': 22,
            'price': Decimal('5.25'),
            'tag': [
                {'name': 'tag_test_name1'},
                {'name': 'tag_test_name2'},
            ],
            'link': 'https://example.com/recipe.pdf'
        }
        response = self.client.post(
            path=RECIPE_URL, data=payload, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.tag.count(), 2)
        self.assertIn(tag, recipe.tag.all())

        for tag in payload['tag']:
            tag_exists = recipe.tag.filter(
                user=self.user,
                name=tag['name']
            ).exists()
            self.assertTrue(tag_exists)

    def test_recipe_update_patch_for_create_tag_successful(self):
        """Test updating recipe for creating tag is successful."""

        recipe = create_recipe(user=self.user)

        url = recipe_detail_url(recipe_id=recipe.id)
        payload = {
            'tag': [
                {'name': 'tag_test_name'}
            ]
        }
        response = self.client.patch(path=url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        new_tag = Tag.objects.get(user=self.user, name='tag_test_name')
        self.assertIn(new_tag, recipe.tag.all())

    def test_recipe_update_patch_for_assign_existing_tag_successful(self):
        """
        Test assigning an existing tag when updating a recipe. successful.
        :return:
        """

        tag_test_1 = Tag.objects.create(
            user=self.user, name='tag_test_name_1'
        )
        recipe = create_recipe(user=self.user)
        recipe.tag.add(tag_test_1)

        tag_test_2 = Tag.objects.create(
            user=self.user, name='tag_test_name_2'
        )

        url = recipe_detail_url(recipe_id=recipe.id)
        payload = {
            'tag': [
                {'name': 'tag_test_name_2'}
            ]
        }
        response = self.client.patch(path=url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(tag_test_2, recipe.tag.all())
        self.assertNotIn(tag_test_1, recipe.tag.all())

    def test_recipe_update_patch_for_clear_tag_successful(self):
        """Test updating recipe for clear tags is successful."""

        tag = Tag.objects.create(
            user=self.user, name='tag_test_name'
        )
        recipe = create_recipe(user=self.user)
        recipe.tag.add(tag)

        url = recipe_detail_url(recipe_id=recipe.id)
        payload = {
            'tag': []
        }
        response = self.client.patch(path=url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tag.count(), 0)
        self.assertNotIn(tag, recipe.tag.all())

    def test_recipe_post_for_create_with_new_ingredients_successful(self):
        """
        Test creating recipe with nested serializer
        new ingredients is successful.
        :return:
        """

        payload = {
            'title': 'Sample Test Recipe Title',
            'description': 'sample test recipe description.',
            'make_time_minutes': 22,
            'price': Decimal('5.25'),
            'ingredients': [
                {'name': 'ingredient_test_name1'},
                {'name': 'ingredient_test_name2'},
            ],
            'link': 'https://example.com/recipe.pdf'
        }
        response = self.client.post(
            path=RECIPE_URL, data=payload, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)

        for ingredient in payload['ingredients']:
            ingredient_exists = recipe.ingredients.filter(
                user=self.user,
                name=ingredient['name']
            ).exists()
            self.assertTrue(ingredient_exists)

    def test_recipe_post_for_create_with_existing_ingredients_successful(self):
        """
        Test creating recipe with nested serializer existing ingredients
         is successful.
        :return:
        """

        ingredient = Ingredient.objects.create(
            user=self.user, name='ingredient_test_name1'
        )

        payload = {
            'title': 'Sample Test Recipe Title',
            'description': 'sample test recipe description.',
            'make_time_minutes': 22,
            'price': Decimal('5.25'),
            'ingredients': [
                {'name': 'ingredient_test_name1'},
                {'name': 'ingredient_test_name2'},
            ],
            'link': 'https://example.com/recipe.pdf'
        }
        response = self.client.post(
            path=RECIPE_URL, data=payload, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient, recipe.ingredients.all())

        for ingredient in payload['ingredients']:
            ingredients_exists = recipe.ingredients.filter(
                user=self.user,
                name=ingredient['name']
            ).exists()
            self.assertTrue(ingredients_exists)

    def test_recipe_update_patch_for_create_ingredients_successful(self):
        """Test updating recipe for creating ingredients is successful."""

        recipe = create_recipe(user=self.user)

        url = recipe_detail_url(recipe_id=recipe.id)
        payload = {
            'ingredients': [
                {'name': 'ingredient_test_name'}
            ]
        }
        response = self.client.patch(path=url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        new_ingredient = Ingredient.objects.get(
            user=self.user, name='ingredient_test_name'
        )
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_recipe_update_for_assign_existing_ingredients_successful(self):
        """
        Test assigning an existing ingredients when updating a recipe
        is successful.
        :return:
        """

        ingredient_test_1 = Ingredient.objects.create(
            user=self.user, name='ingredient_test_name_1'
        )
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient_test_1)

        ingredient_test_2 = Ingredient.objects.create(
            user=self.user, name='ingredient_test_name_2'
        )

        url = recipe_detail_url(recipe_id=recipe.id)
        payload = {
            'ingredients': [
                {'name': 'ingredient_test_name_2'}
            ]
        }
        response = self.client.patch(path=url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient_test_2, recipe.ingredients.all())
        self.assertNotIn(ingredient_test_1, recipe.ingredients.all())

    def test_recipe_update_patch_for_clear_ingredients_successful(self):
        """Test updating recipe for clear ingredients is successful."""

        ingredient = Ingredient.objects.create(
            user=self.user, name='ingredient_test_name'
        )
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        url = recipe_detail_url(recipe_id=recipe.id)
        payload = {
            'ingredients': []
        }
        response = self.client.patch(path=url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)
        self.assertNotIn(ingredient, recipe.ingredients.all())


class ImageUploadTests(TestCase):
    """Tests for the recipe image upload API."""

    def setUp(self) -> None:
        self.client = APIClient()

        self.user = create_user(
            email='test@example.com',
            username='test_user',
            password='test_pass123'
        )
        self.client.force_authenticate(self.user)

        self.recipe = create_recipe(user=self.user)

    def tearDown(self) -> None:
        self.recipe.image.delete()

    def test_post_recipe_for_upload_image_success(self):
        """Test uploading an image to a recipe successful."""

        url = image_upload_url(recipe_id=self.recipe.id)

        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            image = Image.new(mode='RGB', size=(10, 10))
            image.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            response = self.client.post(
                path=url, data=payload, format='multipart'
            )

        self.recipe.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('image', response.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_post_recipe_for_upload_image_error(self):
        """Test uploading invalid image to a recipe."""

        url = image_upload_url(recipe_id=self.recipe.id)
        payload = {'image': 'not_an_image'}
        response = self.client.post(path=url, data=payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
