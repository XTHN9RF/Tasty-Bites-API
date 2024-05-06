from django.urls import path

from .views import (SingleRecipeDetailView,
                    GetMultipleRecipesView,
                    AddNewRecipeView,
                    GetRecipesByIngredientsView,
                    GetIngredientsListView, )

app_name = 'recipes'

urlpatterns = [
    path('recipe/<slug:slug>/', SingleRecipeDetailView.as_view({'get': 'view_single_recipe'}), name='recipe-detail'),
    path('recipes/', GetMultipleRecipesView.as_view({'get': 'view_multiple_recipes'}), name='recipes-list'),
    path('add-recipe/', AddNewRecipeView.as_view({'post': 'create_new_recipe'}), name="add-recipe"),
    path('recipes-by-ingredients/', GetRecipesByIngredientsView.as_view({'post': 'recipes_by_ingredients'}),
         name='recipes-by-ingredients'),
    path('ingredients/', GetIngredientsListView.as_view({'get': 'get_ingredients'}), name='ingredients-list'),
    path('delete-recipe/<slug:slug>/', SingleRecipeDetailView.as_view({'delete': 'delete_recipe'}),
         name='delete-recipe'),
    path('update-recipe/<slug:slug>/', SingleRecipeDetailView.as_view({'put': 'update_recipe'}), name='update-recipe'),
]
