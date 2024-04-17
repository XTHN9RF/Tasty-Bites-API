from django.db import models
from user.models import User
from slugify import slugify


class Recipe(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    cook_time = models.CharField(max_length=100)
    complexity = models.CharField(max_length=100)
    total_price = models.CharField(max_length=100)
    total_calories = models.CharField(max_length=100)

    slug = models.SlugField(unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Recipe, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class RecipeImage(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media/recipe_images/', blank=True)

    def __str__(self):
        return self.recipe.title


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    cost = models.IntegerField()
    calories = models.IntegerField()

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.CharField(max_length=100)

    def __str__(self):
        return self.ingredient
