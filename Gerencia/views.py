from django.shortcuts import render
from rest_framework import viewsets
from Usuarios.models import *
from Usuarios.serializer import *
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
    http_method_names = ['get','patch','put', 'post']
    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [AllowAny]
        return super().get_permissions()

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
    

class VerPersonal(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated,IsGerente]
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    http_method_names = ['get','patch']

    def list(self, request):
        usuarios = Usuario.objects.all()
        serializer = self.serializer_class(usuarios, many=True)
        for i in range(len(usuarios)):
            print(usuarios[i].nro_doc)
            medico = Medico.objects.filter(usuario_id=usuarios[i].nro_doc).first()
            if medico:
                serializer.data[i]["tipo_uduario"] = "medico"
            gestor_th = Gestor_TH.objects.filter(usuario_id=usuarios[i].nro_doc).first()
            if gestor_th:
                serializer.data[i]["tipo_uduario"] = "gestor_th"
            auxiliar = Aux_adm.objects.filter(usuario_id=usuarios[i].nro_doc).first()
            if auxiliar:
                serializer.data[i]["tipo_uduario"] = "auxiliar"
            gerente = Gerente.objects.filter(usuario_id=usuarios[i].nro_doc).first()
            if gerente:
                serializer.data[i]["tipo_uduario"] = "gerente"
            if not medico and not gestor_th and not auxiliar and not gerente:
                serializer.data[i]["tipo_uduario"] = "usuario sin rol"   
        return Response(serializer.data)






