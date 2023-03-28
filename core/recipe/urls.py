"""
URL mapping for the recipe API views.
"""

from rest_framework.routers import DefaultRouter

from recipe.views import RecipeModelViewSet


app_name = 'recipe'


router = DefaultRouter()
router.register('', RecipeModelViewSet, basename='recipe')

urlpatterns = router.urls
