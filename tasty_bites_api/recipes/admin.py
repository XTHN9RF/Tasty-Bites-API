from django.contrib import admin

from .models import (Recipe,
                     Ingredient)

admin.register(Recipe, Ingredient)(admin.ModelAdmin)
