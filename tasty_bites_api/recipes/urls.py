from django.urls import path

from .views import (GetSingleRecipeView,
                    GetMultipleRecipesView,
                    AddNewRecipeView,
                    GetRecipesByIngredientsView)

app_name = 'recipes'

urlpatterns = [
    path('recipe/<slug:slug>/', GetSingleRecipeView.as_view({'get': 'view_single_recipe'}), name='recipe-detail'),
    path('recipes/', GetMultipleRecipesView.as_view({'get': 'view_multiple_recipes'}), name='recipes-list'),
    path('add-recipe/', AddNewRecipeView.as_view({'post': 'create_new_recipe'}), name="add-recipe"),
    path('recipes-by-ingredients/', GetRecipesByIngredientsView.as_view({'post': 'recipes_by_ingredients'}),
         name='recipes-by-ingredients')

]
