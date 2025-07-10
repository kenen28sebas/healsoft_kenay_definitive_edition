from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CentroMedicoViewset, ServicioViewset, CupsViewset , VerPersonal,dashboard_admin

router = DefaultRouter()
router.register(r'centro_medico', CentroMedicoViewset, basename='centro_medico')    
router.register(r'servicio', ServicioViewset, basename='servicio')
router.register(r'cups', CupsViewset, basename='cups')
router.register(r'usuarios',VerPersonal , basename='VerPersonal')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard-admin/', dashboard_admin),
]