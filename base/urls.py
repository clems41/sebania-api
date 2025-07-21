from django.contrib.auth.views import PasswordChangeView
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from base.views.auth import *
from base.views.config import ConfigViewSet
from base.views.contact import ContactViewSet
from base.views.ferme import FermeViewSet
from base.views.parcelle import ParcelleModelViewSet
from base.views.suggestion import SuggestionViewSet
from base.views.tache import TacheModelViewSet
from base.views.vocal import VocalViewSet

router = routers.SimpleRouter()
router.register(r'configurations', ConfigViewSet, basename='configurations')
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'fermes', FermeViewSet, basename='fermes')
router.register(r'parcelles', ParcelleModelViewSet, basename='parcelles')
router.register(r'taches', TacheModelViewSet, basename='taches')
router.register(r'contact', ContactViewSet, basename='contact')
router.register(r'vocaux', VocalViewSet, basename='vocaux')
router.register(r'suggestions', SuggestionViewSet, basename='suggestions')
urlpatterns = router.urls

urlpatterns += [
    path('auth/token/access/', TokenObtainPairView.as_view(), name='get_access_token'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
]
