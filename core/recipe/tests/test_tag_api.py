"""
Tests for the tag APIs.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from config.models import Tag, Recipe

from recipe.serializers import TagModelSerializer

from decimal import Decimal


TAG_URL = reverse('recipe:tag-list')


def tag_detail_url(tag_id):
    """Return a tag detail url."""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(
    email='test@example.com', username='test_user', password='test_pass123'
):
    """Create and return a new user."""
    return get_user_model().objects.create_user(
        email=email,
        username=username,
        password=password
    )


class PublicTagAPITests(TestCase):
    """Test for unauthenticated tag API requests."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_tag_list_auth_required(self):
        """Test auth is required to retrieving tags."""

        response = self.client.get(path=TAG_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagAPITests(TestCase):
    """Test for authenticated tag API requests."""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_tag_get_list_success(self):
        """Test for get tag list API request."""

        Tag.objects.create(user=self.user, name='tag_name')
        Tag.objects.create(user=self.user, name='tag_name2')

        response = self.client.get(path=TAG_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagModelSerializer(tags, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_tag_list_limited_to_authenticated_user(self):
        """Test for tag list limited to authenticated user."""

        other_user = create_user(
            email='other_test@example.com',
            username='other_test_user',
        )

        Tag.objects.create(user=other_user, name='tag_test_name')
        Tag.objects.create(user=self.user, name='tag_test_name2')
        tag = Tag.objects.create(user=self.user, name='tag_test_name3')

        response = self.client.get(path=TAG_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        tags = Tag.objects.filter(user=self.user).order_by('-name')
        serializer = TagModelSerializer(tags, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], tag.name)
        self.assertEqual(response.data[0]['id'], tag.id)

    def test_tag_patch_for_full_update_success(self):
        """Test full update of a tag is successful."""

        tag = Tag.objects.create(user=self.user, name='tag_test_name')

        payload = {'name': 'tag_test_name_edited'}
        url = tag_detail_url(tag_id=tag.id)
        response = self.client.patch(path=url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])
        self.assertEqual(tag.user, self.user)

    def test_tag_delete_success(self):
        """Test deleting a tag successful."""

        tag = Tag.objects.create(user=self.user, name='tag_test_name')
        url = tag_detail_url(tag_id=tag.id)
        response = self.client.delete(path=url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag.id).exists())

    def test_tags_filter_only_assigned_to_recipes(self):
        """Test listing tags by those assigned to recipes."""

        tag1 = Tag.objects.create(
            user=self.user, name='tag test name 1'
        )
        tag2 = Tag.objects.create(
            user=self.user, name='tag test name 2'
        )

        recipe1 = Recipe.objects.create(
            user=self.user,
            title='recipe test title',
            make_time_minutes=55,
            price=Decimal('53.4')
        )
        recipe1.tag.add(tag1)

        params = {'assigned_only': 1}
        response = self.client.get(TAG_URL, params)

        serializer1 = TagModelSerializer(tag1)
        serializer2 = TagModelSerializer(tag2)

        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_tags_filter_unique(self):
        """Test filtered tags returned a unique list."""

        tag = Tag.objects.create(
            user=self.user, name='tag test name 1'
        )
        Tag.objects.create(
            user=self.user, name='tag test name 2'
        )

        recipe1 = Recipe.objects.create(
            user=self.user,
            title='recipe first test title',
            make_time_minutes=55,
            price=Decimal('53.4')
        )
        recipe2 = Recipe.objects.create(
            user=self.user,
            title='recipe second test title',
            make_time_minutes=25,
            price=Decimal('50.4')
        )
        recipe1.tag.add(tag)
        recipe2.tag.add(tag)

        params = {'assigned_only': 1}
        response = self.client.get(TAG_URL, params)

        self.assertEqual(len(response.data), 1)
