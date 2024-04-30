from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from recipes.models import (Recipe,
                            Ingredient)
from user.models import User


class UnauthenticatedRecipesApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username="unauth_test_user")
        self.ingredient1 = Ingredient.objects.create(name='Test Ingredient 1', cost=10, calories=100)
        self.ingredient2 = Ingredient.objects.create(name='Test Ingredient 2', cost=20, calories=200)
        self.recipe = Recipe.objects.create(title='Test Recipe', description='Test Description', author=self.user,
                                            cook_time='30 minutes', complexity='Easy', total_price='30',
                                            total_calories='300')

    def test_recipe_detail(self):
        url = reverse('recipes:recipe-detail', kwargs={'slug': self.recipe.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.recipe.title)
        self.assertEqual(response.data['description'], self.recipe.description)
        self.assertEqual(response.data['author_name'], self.recipe.author.username)
        self.assertEqual(response.data['cook_time'], self.recipe.cook_time)
        self.assertEqual(response.data['complexity'], self.recipe.complexity)
        self.assertEqual(response.data['total_price'], self.recipe.total_price)
        self.assertEqual(response.data['total_calories'], self.recipe.total_calories)
        self.assertEqual(response.data['ingredients'], [])

    def test_recipe_list(self):
        url = reverse('recipes:recipes-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['title'], self.recipe.title)
        self.assertEqual(response.data[0]['description'], self.recipe.description)
        self.assertEqual(response.data[0]['author_name'], self.recipe.author.username)
        self.assertEqual(response.data[0]['cook_time'], self.recipe.cook_time)
        self.assertEqual(response.data[0]['complexity'], self.recipe.complexity)
        self.assertEqual(response.data[0]['total_price'], self.recipe.total_price)
        self.assertEqual(response.data[0]['total_calories'], self.recipe.total_calories)
        self.assertEqual(response.data[0]['ingredients'], [])
        self.assertEqual(len(response.data), 1)

    def test_recipe_creating(self):
        url = reverse('recipes:add-recipe')
        data = {
            'title': 'Failed Test Recipe',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRecipesApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create(username='auth_test_user')
        self.ingredient1 = Ingredient.objects.create(name='Ingredient 1', cost=10, calories=100)
        self.ingredient2 = Ingredient.objects.create(name='Ingredient 2', cost=20, calories=200)
        self.recipe = Recipe.objects.create(title='Test Recipe', description='Test Description', author=self.user,
                                            cook_time='30 minutes', complexity='Easy', total_price='30',
                                            total_calories='300',
                                            ingredients=[self.ingredient1.id, self.ingredient2.id])

        self.client.force_authenticate(user=self.user)

    def test_recipe_creating(self):
        url = reverse('recipes:add-recipe')
        data = {
            'title': 'Test Recipe 2',
            'description': 'Test Description 2',
            'cook_time': '30 minutes',
            'complexity': 'Easy',
            'total_price': '30',
            'total_calories': '300',
            'ingredients': [self.ingredient1.id, self.ingredient2.id]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.recipe.refresh_from_db()
        self.assertEqual(Recipe.objects.count(), 2)
        self.assertEqual(Recipe.objects.get(title='Test Recipe 2').title, 'Test Recipe 2')
        self.assertEqual(Recipe.objects.get(title='Test Recipe 2').description, 'Test Description 2')
        self.assertEqual(Recipe.objects.get(title='Test Recipe 2').author, self.user)
        self.assertEqual(Recipe.objects.get(title='Test Recipe 2').cook_time, '30 minutes')
        self.assertEqual(Recipe.objects.get(title='Test Recipe 2').complexity, 'Easy')
        self.assertEqual(Recipe.objects.get(title='Test Recipe 2').total_price, '30')
        self.assertEqual(Recipe.objects.get(title='Test Recipe 2').total_calories, '300')
        self.assertEqual(Recipe.objects.get(title='Test Recipe 2').ingredients.count(), 2)
        self.assertEqual(Recipe.objects.get(title='Test Recipe 2').ingredients.first(), self.ingredient1)
        self.assertEqual(Recipe.objects.get(title='Test Recipe 2').ingredients.last(), self.ingredient2)
