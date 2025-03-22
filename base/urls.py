from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from base.views.auth import *

router = routers.SimpleRouter()
# router.register(r'configurations', ConfigViewSet)
router.register(r'auth', AuthViewSet, basename='auth')
urlpatterns = router.urls

urlpatterns += [
    path('auth/token/access/', TokenObtainPairView.as_view(), name='get_access_token'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),

    ### CONFIG ###
    # path('configurations/methodes-agricoles', get_all_methode_agricole, name='config'),
    # path('configurations/types-parcelle', get_all_type_parcelle, name='config'),
    # path('configurations/unites', get_all_unites, name='config'),
    # path('configurations/cultures', get_all_cultures, name='config'),
    # path('configurations/activites', get_all_activites, name='config'),
]
