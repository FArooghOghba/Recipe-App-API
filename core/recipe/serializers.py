"""
Serializers for the user API View.
"""

from rest_framework import serializers

from config.models import Recipe, Tag


class TagModelSerializer(serializers.ModelSerializer):
    """Serializer for the tag object."""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class RecipeModelSerializer(serializers.ModelSerializer):
    """Serializer for the recipe object."""

    tag = TagModelSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id',
            'title',
            'make_time_minutes',
            'price',
            'link',
            'tag'
        ]
        read_only_fields = ('id',)

    def create(self, validated_data):
        """Create a Recipe."""

        tags = validated_data.pop('tag', [])
        recipe = Recipe.objects.create(**validated_data)
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag
            )
            recipe.tag.add(tag_obj)

        return recipe


class RecipeDetailModelSerializer(RecipeModelSerializer):
    """Serializer for recipe detail object."""

    class Meta(RecipeModelSerializer.Meta):
        fields = RecipeModelSerializer.Meta.fields + ['description']
