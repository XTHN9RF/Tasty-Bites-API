from rest_framework import serializers

from .models import (Recipe,
                     RecipeImage,
                     Ingredient,
                     IngredientInRecipe)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient model"""
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe model"""
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def create(self, validated_data):
        """Create a new recipe with ingredients"""
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe_image = RecipeImage.objects.create(recipe=recipe, image=validated_data.get('image', None))
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.create(recipe=recipe, **ingredient_data)
            IngredientInRecipe.objects.create(recipe=recipe, ingredient=ingredient)
        return recipe

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


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for RecipeImage model"""
    class Meta:
        model = RecipeImage
        fields = '__all__'

    def update(self, instance, validated_data):
        """Update a recipe image"""
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance
