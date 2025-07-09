from django.contrib import admin
from django.urls import path
from rest_framework import routers
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from Gestion_citas.views import *


router=routers.DefaultRouter()
router.register(r'cita', CitaViewSet)



urlpatterns = [
    path('',include(router.urls))
]
