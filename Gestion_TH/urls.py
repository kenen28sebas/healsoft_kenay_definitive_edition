from django.contrib import admin
from django.urls import path
from rest_framework import routers
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from Gestion_TH.views import *


router=routers.DefaultRouter()
router.register(r'hoja/vida', HojaVistas)
router.register(r'academicos',AcademicoVistas)
router.register(r'experiencia/laboral',ExperienciVistas, basename="experiencia_laboral")
router.register(r'solicitudes',SolicitudActualizacionVistas,basename='solicitudes_hoja')
# router.register(r'cargos',CargoVistas,basename='cargos')
router.register(r'agenda-mes', AgendaMesViewSet, basename="agenda-mes")
router.register(r'agenda-dia', AgendaDiaViewSet, basename="agenda-dia")


urlpatterns = [
    path('',include(router.urls)),
    path("dashboard_gestor_th/" , dashboard_gestor_th)
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)