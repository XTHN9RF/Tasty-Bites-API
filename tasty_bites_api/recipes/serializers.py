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

    def update(self, instance, validated_data):
        """Update a recipe with ingredients"""
        ingredients_data = validated_data.pop('ingredients')
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.create(recipe=instance, **ingredient_data)
            IngredientInRecipe.objects.create(recipe=instance, ingredient=ingredient)
        return instance


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Serializer for IngredientInRecipe model"""

    class Meta:
        model = IngredientInRecipe
        fields = ('recipe', 'ingredient', 'amount')


class RecipeCreationSerializer(serializers.ModelSerializer):
    """Serializer for Recipe model"""
    ingredients = serializers.ListField(child=serializers.IntegerField())
    image = RecipeImageSerializer(many=False, required=False)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Recipe
        fields = (
            'image', 'title', 'author', 'description', 'ingredients', 'cook_time', 'complexity', 'total_price',
            'total_calories')

    def create(self, validated_data):
        """Create a new recipe with ingredients"""
        ingredient_ids = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_id in ingredient_ids:
            ingredient = Ingredient.objects.get(pk=ingredient_id)
            IngredientInRecipe.objects.create(recipe=recipe, ingredient=ingredient)
        return recipe
