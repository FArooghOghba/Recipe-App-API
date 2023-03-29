"""
URL mapping for the recipe API views.
"""

from rest_framework.routers import DefaultRouter

from recipe.views import (
    RecipeModelViewSet,
    TagGenericViewSet
)


app_name = 'recipe'


router = DefaultRouter()
router.register('recipe', RecipeModelViewSet, basename='recipe')
router.register('tag', TagGenericViewSet, basename='tag')

urlpatterns = router.urls
