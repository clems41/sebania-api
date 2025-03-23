from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from base.views.auth import *
from base.views.config import ConfigViewSet

router = routers.SimpleRouter()
router.register(r'configurations', ConfigViewSet, basename='configurations')
router.register(r'auth', AuthViewSet, basename='auth')
urlpatterns = router.urls

urlpatterns += [
    path('auth/token/access/', TokenObtainPairView.as_view(), name='get_access_token'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
]
