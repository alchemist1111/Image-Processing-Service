from django.urls import path
from .views import UserRegistrationView, UserLoginView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    # JWT token obtain url
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User registration url
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    
    # User login url
    path('login/', UserLoginView.as_view(), name='user-login'),
]