from django.contrib import admin
from .models import User
from .models import UserAvatar

admin.register(User, UserAvatar)(admin.ModelAdmin)
