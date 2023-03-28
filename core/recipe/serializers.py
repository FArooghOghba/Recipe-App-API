"""
Serializers for the user API View.
"""

from rest_framework import serializers

from config.models import Recipe


class RecipeModelSerializer(serializers.ModelSerializer):
    """Serializer for the recipe object."""

    class Meta:
        model = Recipe
        fields = [
            'id',
            'title',
            'make_time_minutes',
            'price',
            'link',
        ]
        read_only_fields = ('id',)


class RecipeDetailModelSerializer(RecipeModelSerializer):
    """Serializer for recipe detail object."""

    class Meta(RecipeModelSerializer.Meta):
        fields = RecipeModelSerializer.Meta.fields + ['description']
