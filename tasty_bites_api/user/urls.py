from django.urls import (path,
                         include)

from dj_rest_auth import views as dj_rest_auth_views

namespace = 'user'

urlpatterns = [
    path('registration/', include('dj_rest_auth.registration.urls')),
    path('auth/', include('dj_rest_auth.urls')),
    path('password/reset/confirm/<uidb64>/<token>/', dj_rest_auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
]
