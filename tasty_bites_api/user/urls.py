from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserRegistrationView
from .views import UserLoginView
from .views import UserProfileView
from .views import UserUpdateView
from .views import UserPasswordResetView

app_name = 'user'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/<str:username>/', UserProfileView.as_view(), name='user_profile'),
    path('profile/', UserProfileView.as_view(), name='your_profile'),
    path('update/', UserUpdateView.as_view({'put': 'update_profile'}), name='update_profile'),
    path('reset-password/', UserPasswordResetView.as_view({'post': 'reset_password'}), name='reset_password'),
]
