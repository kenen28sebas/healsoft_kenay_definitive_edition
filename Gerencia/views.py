from django.shortcuts import render
from rest_framework import viewsets
from .models import Centro_medico, Servicio, Cups
from .serializer import Centro_medicoSerializer, ServicioSerializer, CupsSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny , BasePermission
from Usuarios.models import Gerente
from rest_framework.response import Response
# Create your views here.

class IsGerente(BasePermission):
    def has_permission(self, request, view):
        isTrue = False
        gerenete = Gerente.objects.filter(usuario_id = request.user.nro_doc)
        if gerenete:
            isTrue =True
        return isTrue


class CentroMedicoViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated,IsGerente]
    queryset = Centro_medico.objects.all()
    serializer_class = Centro_medicoSerializer

class ServicioViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated,IsGerente]
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer
    http_method_names = ['get','patch']
    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [AllowAny]
        return super().get_permissions()
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()  # Obtiene el pservicio por ID
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        cups = Cups.objects.filter(servicio_id = instance.capitulo)
        if bool(request.data['estado']) == False:
            for cup in cups:
                print(cup.estado)
                print(cup.codigo)
                print(cup.nombre)
                cup.estado = False
                cup.save()
        if bool(request.data['estado']) == True:
            for cup in cups:
                print(cup.estado)
                print(cup.codigo)
                print(cup.nombre)
                cup.estado = True
                cup.save()
        
        return Response(serializer.data)

class CupsViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated,IsGerente]
    queryset = Cups.objects.all()
    serializer_class = CupsSerializer
    http_method_names = ['get','patch']
    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [AllowAny]
        return super().get_permissions()
    

    




