"""
URL configuration for healtsoft project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from Usuarios.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('registrar/roles',registrar_roles,name='registrar_roles'),
    path("resgistrar/gerente/" , registrar_gerente, name="registrar_gerente"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
    path("actualizar_datos/", actualizar_datos, name="actualizar_datos"),
    path("activar_usuario/", activar_usuario, name="activar_usuario"),
    path("api/gerente/", include('Gerencia.urls')),
    path("api/gestor_th/", include('Gestion_TH.urls'))
]
