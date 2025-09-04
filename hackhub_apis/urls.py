from django.urls import path,include
from .views import *
from django.conf.urls.static import static
from django.conf import settings
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users',CustomUserViewSet,basename='user')
router.register(r'posts',PostViewSet,basename='posts')

urlpatterns = [
    path('api/token/',TokenObtainPairView.as_view(),name="token_obtain_api"),
    path('api/token/refresh/',TokenRefreshView.as_view(),name="token_refresh_api"),
    path('auth/verify/email/',EmailVerificationAPI.as_view(),name="verify-email"),
    path('logout_api/',LogoutAPI.as_view(),name="logout_api")
] + router.urls