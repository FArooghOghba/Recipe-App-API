"""
Views for the recipe APIs.
"""

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from config.models import Recipe, Tag, Ingredient
from recipe.serializers import (
    RecipeModelSerializer,
    RecipeDetailModelSerializer,
    RecipeImageModelSerializer,
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
        elif self.action == 'upload_image':
            return RecipeImageModelSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""

        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseRecipeAttrGenericViewSet(
        mixins.DestroyModelMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet
):
    """Base view set for recipe attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""

        return self.queryset.filter(
            user=self.request.user
        ).order_by('-name')


class TagGenericViewSet(BaseRecipeAttrGenericViewSet):
    """Retrieve tags for specifics authenticated user."""

    serializer_class = TagModelSerializer
    queryset = Tag.objects.all()


class IngredientGenericViewSet(BaseRecipeAttrGenericViewSet):
    """Retrieve ingredients for specifics authenticated user."""

    serializer_class = IngredientModelSerializer
    queryset = Ingredient.objects.all()
