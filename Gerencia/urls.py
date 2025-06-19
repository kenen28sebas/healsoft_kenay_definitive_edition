from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CentroMedicoViewset, ServicioViewset, CupsViewset

router = DefaultRouter()
router.register(r'centro_medico', CentroMedicoViewset, basename='centro_medico')    
router.register(r'servicio', ServicioViewset, basename='servicio')
router.register(r'cups', CupsViewset, basename='cups')
urlpatterns = [
    path('', include(router.urls)),
]