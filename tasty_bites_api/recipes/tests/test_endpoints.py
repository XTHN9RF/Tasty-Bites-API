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
        self.ingredient3 = Ingredient.objects.create(name='Test Ingredient 3', cost=30, calories=300)

        self.recipe = Recipe.objects.create(title='Test Recipe', description='Test Description', author=self.user,
                                            cook_time='30 minutes', complexity='Easy', total_price='30',
                                            total_calories='300')

        self.recipe2 = Recipe.objects.create(title='Test Recipe 2', description='Test Description 2', author=self.user,
                                             cook_time='30 minutes', complexity='Easy', total_price='30',
                                             total_calories='300')

        self.recipe.ingredients.set([self.ingredient1, self.ingredient2])
        self.recipe2.ingredients.set([self.ingredient2, self.ingredient3])

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
        self.assertEqual(len(response.data['ingredients']), 2)

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
        self.assertEqual(len(response.data[0]['ingredients']), 2)
        self.assertEqual(len(response.data), 2)

    def test_recipe_creating(self):
        url = reverse('recipes:add-recipe')
        data = {
            'title': 'Failed Test Recipe',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_recipes_by_ingredients(self):
        url = reverse('recipes:recipes-by-ingredients')
        data = {
            'ingredients': [self.ingredient1.slug, self.ingredient2.slug]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['description'], self.recipe.description)
        self.assertEqual(response.data[0]['cook_time'], self.recipe.cook_time)
        self.assertEqual(response.data[0]['total_price'], self.recipe.total_price)
        self.assertEqual(response.data[0]['total_calories'], self.recipe.total_calories)
        self.assertEqual(response.data[0]['complexity'], self.recipe.complexity)
        self.assertEqual(response.data[0]['ingredients'][0]['name'], self.ingredient1.name)
        self.assertEqual(response.data[0]['ingredients'][1]['name'], self.ingredient2.name)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['ingredients'][0]['cost'], self.ingredient1.cost)
        self.assertEqual(response.data[0]['ingredients'][1]['cost'], self.ingredient2.cost)
        self.assertEqual(response.data[0]['author_name'], self.recipe.author.username)
        self.assertEqual(response.data[0]['ingredients'][0]['calories'], self.ingredient1.calories)
        self.assertEqual(response.data[0]['ingredients'][1]['calories'], self.ingredient2.calories)
        self.assertEqual(response.data[0]['title'], self.recipe.title)

    def test_ingredients_list(self):
        url = reverse('recipes:ingredients-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], self.ingredient1.name)
        self.assertEqual(response.data[0]['cost'], self.ingredient1.cost)
        self.assertEqual(response.data[0]['calories'], self.ingredient1.calories)
        self.assertEqual(response.data[1]['name'], self.ingredient2.name)
        self.assertEqual(response.data[1]['cost'], self.ingredient2.cost)
        self.assertEqual(response.data[1]['calories'], self.ingredient2.calories)
        self.assertEqual(response.data[2]['name'], self.ingredient3.name)
        self.assertEqual(response.data[2]['cost'], self.ingredient3.cost)
        self.assertEqual(response.data[2]['calories'], self.ingredient3.calories)
        self.assertEqual(len(response.data), 3)


class AuthenticatedRecipesApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create(username='auth_test_user')
        self.ingredient1 = Ingredient.objects.create(name='Ingredient 1', cost=10, calories=100)
        self.ingredient2 = Ingredient.objects.create(name='Ingredient 2', cost=20, calories=200)
        self.recipe = Recipe.objects.create(title='Test Recipe', description='Test Description', author=self.user,
                                            cook_time='30 minutes', complexity='Easy', total_price='30',
                                            total_calories='300',
                                            )
        self.recipe.ingredients.set([self.ingredient1, self.ingredient2])
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
            'ingredients': [self.ingredient1.slug, self.ingredient2.slug]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.recipe.refresh_from_db()
        self.assertEqual(Recipe.objects.count(), 2)
        self.assertEqual(Recipe.objects.get(title=data['title']).title, data['title'])
        self.assertEqual(Recipe.objects.get(title=data['title']).description, data['description'])
        self.assertEqual(Recipe.objects.get(title=data['title']).cook_time, data['cook_time'])
        self.assertEqual(Recipe.objects.get(title=data['title']).complexity, data['complexity'])
        self.assertEqual(Recipe.objects.get(title=data['title']).total_price, data['total_price'])
        self.assertEqual(Recipe.objects.get(title=data['title']).total_calories, data['total_calories'])
        self.assertEqual(Recipe.objects.get(title=data['title']).ingredients.count(), 2)
        self.assertEqual(Recipe.objects.get(title=data['title']).ingredients.first(), self.ingredient1)
        self.assertEqual(Recipe.objects.get(title=data['title']).ingredients.last(), self.ingredient2)
        self.assertEqual(Recipe.objects.get(title=data['title']).author, self.user)
        self.assertEqual(Recipe.objects.get(title=data['title']).author.username, self.user.username)

    def test_recipe_delete(self):
        url = reverse('recipes:delete-recipe', kwargs={'slug': self.recipe.slug})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Recipe.objects.count(), 0)

    def test_recipe_update(self):
        url = reverse('recipes:update-recipe', kwargs={'slug': self.recipe.slug})
        data = {
            'title': 'Test Recipe change',
            'description': 'Test Description change',
            'cook_time': '10 minutes',
            'complexity': 'Hard',
            'total_price': '3000',
            'total_calories': '300000',
            'ingredients': [self.ingredient1.slug, self.ingredient1.slug]
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.recipe.refresh_from_db()
        self.assertEqual(Recipe.objects.count(), 1)
        self.assertEqual(self.recipe.title, data['title'])
        self.assertEqual(self.recipe.description, data['description'])
        self.assertEqual(self.recipe.cook_time, data['cook_time'])
        self.assertEqual(self.recipe.complexity, data['complexity'])
        self.assertEqual(self.recipe.total_price, data['total_price'])
        self.assertEqual(self.recipe.total_calories, data['total_calories'])
        self.assertEqual(self.recipe.ingredients.count(), 1)
        self.assertEqual(self.recipe.ingredients.first(), self.ingredient1)
        self.assertEqual(self.recipe.ingredients.last(), self.ingredient1)
        self.assertEqual(self.recipe.author, self.user)
        self.assertEqual(self.recipe.author.username, self.user.username)
