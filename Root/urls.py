from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'alertlimits', AlertLimitsViewSet, basename='alertlimits')
router.register(r'alerts', AlertViewSet, basename='alerts')
router.register(r'areas', AreaViewSet, basename='areas')
router.register(r'bearinglocations', BearingLocationViewSet, basename='bearinglocations')
router.register(r'customers', CustomerViewSet, basename='customers')
router.register(r'machinehealth', MachineHealthViewSet, basename='machinehealth')
router.register(r'machines', MachineViewSet, basename='machines')
router.register(r'orientations', OrientationViewSet, basename='orientations')
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('example/', ExampleView.as_view(), name='examplelogin'),
    path('tokenrefresh/', TokenRefreshView.as_view(), name='tokenrefresh'),
]

""" for url in urlpatterns:
    print(f"URL: {url}") """