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
router.register(r'team_opportunity',TeamOpportunityViewSet,basename="team-opportunity")

urlpatterns = [
    path('api/token/',TokenObtainPairView.as_view(),name="token_obtain_api"),
    path('api/token/refresh/',TokenRefreshView.as_view(),name="token_refresh_api"),
    path('auth/verify/email/',EmailVerificationAPI.as_view(),name="verify-email"),
    path('logout_api/',LogoutAPI.as_view(),name="logout_api"),
    path('who_am_i_api/',WhoAmIAPI.as_view(),name="who-am-i-api")
] + router.urls