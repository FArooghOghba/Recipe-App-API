"""
Serializers for the user API View.
"""

from rest_framework import serializers

from config.models import Recipe, Tag, Ingredient


class TagModelSerializer(serializers.ModelSerializer):
    """Serializer for the tag object."""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class IngredientModelSerializer(serializers.ModelSerializer):
    """Serializer for the ingredient object."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name')
        read_only_fields = ('id',)


class RecipeModelSerializer(serializers.ModelSerializer):
    """Serializer for the recipe object."""

    tag = TagModelSerializer(many=True, required=False)
    ingredients = IngredientModelSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id',
            'title',
            'make_time_minutes',
            'price',
            'link',
            'ingredients',
            'tag'
        ]
        read_only_fields = ('id',)

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""

        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag
            )
            recipe.tag.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients as needed."""

        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient
            )
            recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        """Create a Recipe."""

        tags = validated_data.pop('tag', [])
        ingredients = validated_data.pop('ingredients', [])

        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(
            tags=tags, recipe=recipe
        )
        self._get_or_create_ingredients(
            ingredients=ingredients, recipe=recipe
        )

        return recipe

    def update(self, instance, validated_data):
        """Updating a recipe object."""

        tags = validated_data.pop('tag', None)
        ingredients = validated_data.pop('ingredients', None)

        if tags is not None:
            instance.tag.clear()
            self._get_or_create_tags(tags=tags, recipe=instance)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(
                ingredients=ingredients, recipe=instance
            )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailModelSerializer(RecipeModelSerializer):
    """Serializer for recipe detail object."""

    class Meta(RecipeModelSerializer.Meta):
        fields = RecipeModelSerializer.Meta.fields + ['description', 'image']


class RecipeImageModelSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes."""

    class Meta:
        model = Recipe
        fields = ('id', 'image')
        read_only_fields = ('id',)
        extra_kwargs = {'image': {'required': True}}
