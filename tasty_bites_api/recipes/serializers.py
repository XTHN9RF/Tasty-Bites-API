from rest_framework import serializers

from .models import (Recipe,
                     RecipeImage,
                     Ingredient,
                     IngredientInRecipe)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient model"""

    class Meta:
        model = Ingredient
        fields = ('name', 'cost', 'calories')


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for RecipeImage model"""

    class Meta:
        model = RecipeImage
        fields = ('image',)

    def update(self, instance, validated_data):
        """Update a recipe image"""
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe model"""
    ingredients = IngredientSerializer(many=True)
    author_name = serializers.CharField(source='author.username')
    image = RecipeImageSerializer(many=False)

    class Meta:
        model = Recipe
        fields = (
            'image', 'title', 'author_name', 'description', 'ingredients', 'cook_time', 'complexity', 'total_price',
            'total_calories', 'created_at')


class RecipeUpdateSerializer(serializers.ModelSerializer):
    """Serializer for Recipe model"""
    ingredients = serializers.ListField(child=serializers.CharField())
    image = RecipeImageSerializer(many=False, required=False)

    class Meta:
        model = Recipe
        fields = (
            'image', 'title', 'description', 'ingredients', 'cook_time', 'complexity', 'total_price',
            'total_calories')

    def update(self, instance, validated_data):
        """Update a recipe with ingredients"""
        ingredient_slugs = validated_data.pop('ingredients')
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.cook_time = validated_data.get('cook_time', instance.cook_time)
        instance.complexity = validated_data.get('complexity', instance.complexity)
        instance.total_price = validated_data.get('total_price', instance.total_price)
        instance.total_calories = validated_data.get('total_calories', instance.total_calories)
        instance.save()
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        for ingredient_slug in ingredient_slugs:
            ingredient = Ingredient.objects.get(slug=ingredient_slug)
            IngredientInRecipe.objects.update_or_create(recipe=instance, ingredient=ingredient)
        return instance


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Serializer for IngredientInRecipe model"""

    class Meta:
        model = IngredientInRecipe
        fields = ('recipe', 'ingredient', 'amount')


class RecipeCreationSerializer(serializers.ModelSerializer):
    """Serializer for Recipe model"""
    ingredients = serializers.ListField(child=serializers.CharField())
    image = RecipeImageSerializer(many=False, required=False)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Recipe
        fields = (
            'image', 'title', 'author', 'description', 'ingredients', 'cook_time', 'complexity', 'total_price',
            'total_calories')

    def create(self, validated_data):
        """Create a new recipe with ingredients"""
        ingredient_slugs = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_slug in ingredient_slugs:
            ingredient = Ingredient.objects.get(slug=ingredient_slug)
            IngredientInRecipe.objects.create(recipe=recipe, ingredient=ingredient)
        return recipe
