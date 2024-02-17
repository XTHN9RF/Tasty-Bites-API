from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserRegistrationView
from .views import UserLoginView

namespace = 'user'

urlpatterns = [
    path('/register/', UserRegistrationView.as_view(), name='register'),
    path('/login/', UserLoginView.as_view(), name='login'),
    path('/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
