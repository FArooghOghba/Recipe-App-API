"""
Views for the recipe APIs.
"""

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from config.models import Recipe, Tag, Ingredient
from recipe.serializers import (
    RecipeModelSerializer,
    RecipeDetailModelSerializer,
    TagModelSerializer,
    IngredientModelSerializer
)


class RecipeModelViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""

    serializer_class = RecipeDetailModelSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for specifics authenticated user."""

        return self.queryset.filter(
            user=self.request.user
        ).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""

        if self.action == 'list':
            return RecipeModelSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""

        serializer.save(user=self.request.user)


class TagGenericViewSet(
        mixins.DestroyModelMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet
):
    """Retrieve tags for specifics authenticated user."""

    serializer_class = TagModelSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""

        return self.queryset.filter(
            user=self.request.user
        ).order_by('-name')


class IngredientGenericViewSet(
        mixins.DestroyModelMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet
):
    """Retrieve ingredients for specifics authenticated user."""

    serializer_class = IngredientModelSerializer
    queryset = Ingredient.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""

        return self.queryset.filter(
            user=self.request.user
        ).order_by('-name')
