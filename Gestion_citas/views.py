from django.shortcuts import render
from rest_framework import viewsets
from .serializer import *
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated,BasePermission
from Usuarios.models import Auxiliar, Paciente ,Medico
from Gerencia.models import Servicio,Centro_medico


    
class IsAuxiliar(BasePermission):
    def has_permission(self, request, view):
        isTrue = False
        auxiliar = Auxiliar.objects.filter(usuario_id = request.user.nro_doc)
        if auxiliar:
            isTrue = True
        return isTrue    


class CitaViewSet(viewsets.ModelViewSet):
    serializer_class = CitaSerializer
    queryset = Cita.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAuxiliar]
    http_method_names = ['get', 'post', 'patch']

    def list(self, request):
        nro_doc = request.query_params.get('nro_doc', None)
        if nro_doc:
            paciente = Paciente.objects.filter(usuario_id=nro_doc).first()
            if paciente:
                citas = Cita.objects.filter(paciente=paciente)
            else:
                citas = Cita.objects.none() 
        else:
            citas = Cita.objects.all()  
        serializer = self.serializer_class(citas, many=True)
        return Response(serializer.data)

        

    def create(self, request):
        paciente = Paciente.objects.filter(usuario_id=request.data.get('nro_doc')).first()
        if not paciente:    
            return Response({"error": "Paciente not found"}, status=404)
        medico = Medico.objects.filter(usuario_id=request.data.get('medico_id')).first()
        if not medico:  
            return Response({"error": "Medico not found"}, status=404)
        servicio = Servicio.objects.filter(id=request.data.get('servicio_id')).first()
        if not servicio:  
            return Response({"error": "Servicio not found"}, status=404)
        centro_medico = Centro_medico.objects.filter(id=request.data.get('centro_medico_id')).first()
        if not centro_medico:  
            return Response({"error": "Centro Medico not found"}, status=404)
        datos_cita = {
            'fecha_asignacion': request.data.get('fecha_asignacion'),
            'fecha_solicitud': request.data.get('fecha_solicitud'),
            'estado': request.data.get('estado'),
            'especialidad': request.data.get('especialidad'),
            'tipo_atencion': request.data.get('tipo_atencion'),
            'centro_medico': centro_medico,
            'medico': medico,
            'paciente': paciente,
            'servicio': servicio
        }   
        serializer = self.serializer_class(data=datos_cita)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        if serializer.is_valid():
            cita = serializer.save()
            return Response(self.serializer_class(cita).data, status=201)

    def partial_update(self, request, pk=None):
        cita = self.get_object()
        serializer = self.serializer_class(cita, data=request.data, partial=True)
        if serializer.is_valid():
            cita = serializer.save()
            return Response(self.serializer_class(cita).data)


class InfoCambioViewSet(viewsets.ModelViewSet):
    serializer_class = InfoCambioSerializer
    queryset = Info_cambio.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAuxiliar]
    http_method_names = ['get', 'post', 'patch']

    def create(self, request):
        cita = Cita.objects.filter(id=request.data.get('cita_id')).first()
        if not cita:
            return Response({"error": "Cita not found"}, status=404)
        datos_info_cambio = {
            'fecha_cambio': request.data.get('fecha_cambio'),
            'tipo_cambio': request.data.get('tipo_cambio'),
            'observacion': request.data.get('observacion'),
            'cita': cita
        }
        serializer = self.serializer_class(data=datos_info_cambio)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        if serializer.is_valid():
            info_cambio = serializer.save()
            return Response(self.serializer_class(info_cambio).data, status=201)