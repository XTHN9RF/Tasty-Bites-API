from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action

from common.utils import HttpMethods

from .models import Recipe, Ingredient
from .serializers import (RecipeSerializer,
                          IngredientSerializer,
                          RecipeCreationSerializer)


class GetSingleRecipeView(ViewSet):
    """View that returns information about single recipe"""
    permission_classes = [AllowAny]
    serializer_class = RecipeSerializer

    @action(methods=[HttpMethods.GET.value], detail=False)
    def view_single_recipe(self, request, slug):
        """Method that generates response for GET"""
        recipe = Recipe.objects.get(slug=slug)
        serializer = self.serializer_class(recipe)
        return Response(serializer.data, status=200)


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
                print('i should have saved it')

                return Response("Recipe created successfully", status=201)
            print(serializer.errors)
            return Response(serializer.errors, status=400)
        return Response("User is not exist", status=403)
