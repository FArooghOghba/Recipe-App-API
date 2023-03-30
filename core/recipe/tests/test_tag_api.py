"""
Tests for the tag APIs.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from config.models import Tag

from recipe.serializers import TagModelSerializer


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
