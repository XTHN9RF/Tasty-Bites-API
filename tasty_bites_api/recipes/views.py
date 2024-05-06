from django.db.models import Count
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from common.permissions import IsObjectOwnerOrReadOnly
from common.utils import HttpMethods

from .models import Recipe, Ingredient
from .serializers import (RecipeSerializer,
                          IngredientSerializer,
                          RecipeCreationSerializer,
                          RecipeUpdateSerializer)


class SingleRecipeDetailView(ViewSet):
    """View that returns information about single recipe"""
    permission_classes = [AllowAny, IsObjectOwnerOrReadOnly]
    serializer_class = RecipeSerializer

    def get_serializer_class(self):
        """Method that returns serializer class"""
        if self.request.method == HttpMethods.PUT.value:
            return RecipeUpdateSerializer
        return self.serializer_class

    @action(methods=[HttpMethods.GET.value], detail=False)
    def view_single_recipe(self, request, slug):
        """Method that generates response for GET"""
        recipe = Recipe.objects.get(slug=slug)
        serializer = self.get_serializer_class()(recipe)
        return Response(serializer.data, status=200)

    @action(methods=HttpMethods.PUT.value, detail=False)
    def update_recipe(self, request, slug):
        """Method that updates recipe with given slug"""
        user = self.request.user
        if user:
            recipe = Recipe.objects.get(slug=slug)
            serializer = self.get_serializer_class()(recipe, data=request.data, context={'request': request})
            if serializer.is_valid():
                recipe = serializer.update(recipe, serializer.validated_data)
                recipe.save()

                return Response("Recipe updated successfully", status=200)
            print(serializer.errors)
            return Response(serializer.errors, status=400)
        return Response("User is not exist", status=403)

    @action(methods=HttpMethods.DELETE.value, detail=False)
    def delete_recipe(self, request, slug):
        """Method that deletes recipe with given slug"""
        user = self.request.user
        if user:
            recipe = Recipe.objects.get(slug=slug)
            recipe.delete()
            return Response("Recipe deleted successfully", status=200)
        return Response("User is not exist", status=403)


class GetMultipleRecipesView(ViewSet):
    """View that returns information about multiple recipes"""
    permission_classes = [AllowAny]

    @action(methods=[HttpMethods.GET.value], detail=False)
    def view_multiple_recipes(self, request):
        """Method that generates response for GET"""
        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data, status=200)


class AddNewRecipeView(ViewSet):
    """View that allows to create recipe"""
    permission_classes = [IsAuthenticated]
    serializer_class = RecipeCreationSerializer

    @action(methods=HttpMethods.POST.value, detail=False)
    def create_new_recipe(self, request):
        """Method that created recipe with given information"""
        user = self.request.user
        if user:
            serializer = self.serializer_class(data=request.data, context={'request': request})
            if serializer.is_valid():
                recipe = serializer.create(serializer.validated_data)
                recipe.save()

                return Response("Recipe created successfully", status=201)
            return Response(serializer.errors, status=400)
        return Response("User is not exist", status=403)


class GetRecipesByIngredientsView(ViewSet):
    """View that returns recipes that contain given ingredients"""
    permission_classes = [AllowAny]
    serializer_class = RecipeSerializer

    @action(methods=[HttpMethods.POST.value], detail=True)
    def recipes_by_ingredients(self, request):
        ingredients_slugs = self.request.data.get('ingredients')

        recipes = Recipe.objects.filter(ingredients__slug__in=ingredients_slugs)

        recipes = recipes.annotate(match_count=Count('ingredients'))

        filtered_recipes = recipes.filter(match_count=len(ingredients_slugs))

        serializer = self.serializer_class(filtered_recipes, many=True)

        return Response(serializer.data, status=200)


class GetIngredientsListView(ViewSet):
    """View that returns list of ingredients"""
    permission_classes = [AllowAny]
    serializer_class = IngredientSerializer

    @action(methods=[HttpMethods.GET.value], detail=False)
    def get_ingredients(self, request):
        ingredients = Ingredient.objects.all()
        serializer = self.serializer_class(ingredients, many=True)
        return Response(serializer.data, status=200)
