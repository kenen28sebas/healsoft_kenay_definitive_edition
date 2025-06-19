from django.shortcuts import render

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action


from .utils import generar_pdf_historia_clinica
from .utils import generar_pdf_formula_medica, generar_pdf_orden_procedimiento

from django.conf import settings
import os

import base64
#

from .models import *
from .serializer import *
# Create your views here.


from rest_framework import status
from rest_framework.response import Response

#
from drf_spectacular.utils import extend_schema




# con esta funcion lo que se busca es, no permitir la eliminacion ni la actualizacion de una tabla de la historia clinica

class SoloMedicos(BasePermission):
    message = "No tiene permisos para realizar esta acción."

    def has_permission(self, request, view):
        try:
            es_medico = Medico.objects.filter(usuario=request.user).exists()
            if es_medico:
                return True
            self.message = f"Señor(a) {request.user.first_name} {request.user.last_name}, usted no tiene permisos para realizar registros en Historia Clínica."
            return False
        except Exception:
            self.message = "Error al verificar permisos de usuario."
            return False



class CupsViewSet(viewsets.ReadOnlyModelViewSet):
        serializer_class = CupsSerializer
        queryset = Cups.objects.all()

        # Sobrescribe el método list para devolver solo ciertos campos
        def list(self, request, *args, **kwargs):
            cups = Cups.objects.all().values('id', 'codigo_cups', 'nombre_cups')
            return Response(cups)



class Cie10Viewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = Cie10Serializer
    queryset = Cie10.objects.all()

    # Sobrescribe el método list para devolver solo ciertos campos
    def list(self, request, *args, **kwargs):
        cie10 = Cie10.objects.all().values('id', 'codigo_cie10', 'nombre_cie10')
        return Response(cie10)


class AnamnesisViewset(viewsets.ModelViewSet):
    serializer_class = AnamnesisSerializer
    queryset = Anamnesis.objects.all()
    http_method_names = ['get', 'post']

    def create(self, request):
        # Validar y guardar los datos recibidos
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'Anamnesis creado con éxito', 'data': serializer.data})


class SignosVitalesViewset(viewsets.ModelViewSet):
    serializer_class = SignosVitalesSerializer
    queryset = SignosVitales.objects.all()
    http_method_names = ['get', 'post']

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'Signos Registrados con Éxito', 'data': serializer.data})


class ParaclinicosViewset(viewsets.ModelViewSet):
    serializer_class = ParaclinicosSerializer
    queryset = Paraclinicos.objects.all()
    http_method_names = ['get', 'post']

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'Exámenes Registrados con Éxito', 'data': serializer.data})


class DiagnosticoViewset(viewsets.ModelViewSet):
    serializer_class = DiagnosticoSerializer
    queryset = Diagnostico.objects.all()
    http_method_names = ['get', 'post']

    def create(self, request):
        # Validamos si el código CIE10 existe
        cie10_codigo = request.data.get("cie10")
        try:
            Cie10.objects.get(codigo_cie10=cie10_codigo)
        except Cie10.DoesNotExist:
            return Response({"error": "Código CIE10 no encontrado"}, status=404)

        # Si existe, validamos y guardamos el diagnóstico
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'Diagnóstico Registrado con Éxito', 'data': serializer.data})


class OrdenDeProcedimientosViewset(viewsets.ModelViewSet):
    serializer_class = OrdenDeProcedimientosSerializer
    queryset = OrdenDeProcedimientos.objects.all()
    http_method_names = ['get', 'post']

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        orden = serializer.save() 

        # Generar PDF
        pdf_buffer = generar_pdf_orden_procedimiento(orden)
        pdf_path = os.path.join(settings.MEDIA_ROOT, f"orden_procedimiento_{orden.id}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf_buffer.read())

        return Response({
            'status': 'Orden de procedimiento creada con éxito',
            'orden_de_procedimiento': self.get_serializer(orden).data,
            'pdf_url': request.build_absolute_uri(f"{settings.MEDIA_URL}orden_procedimiento_{orden.id}.pdf")
        }, status=status.HTTP_201_CREATED)


class FormulaMedicaViewset(viewsets.ModelViewSet):
    serializer_class = FormulaMedicaSerializer
    queryset = FormulaMedica.objects.all()
    http_method_names = ['get', 'post']


    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        formula = serializer.save()

        # Generar PDF
        pdf_buffer = generar_pdf_formula_medica(formula)
        pdf_path = os.path.join(settings.MEDIA_ROOT, f"formula_medica_{formula.id}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf_buffer.read())

        return Response({
            'status': 'Fórmula médica creada con éxito',
            'formula_medica': self.get_serializer(formula).data,
            'pdf_url': request.build_absolute_uri(f"{settings.MEDIA_URL}formula_medica_{formula.id}.pdf")
        }, status=status.HTTP_201_CREATED)


class MedicamentoViewset(viewsets.ModelViewSet):
    serializer_class = MedicamentoSerializer
    queryset = Medicamento.objects.all()
    http_method_names = ['get', 'post']

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'Medicamento Registrado con Éxito', 'data': serializer.data})


class EvolucionViewset(viewsets.ModelViewSet):
    serializer_class = EvolucionSerializer
    queryset = Evolucion.objects.all()
    http_method_names = ['get', 'post']

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'Evolución Registrada con Éxito', 'data': serializer.data})


class HistoriaClinicaViewset(viewsets.ModelViewSet):
    serializer_class = HistoriaClinicaSerializer
    queryset = HistoriaClinica.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, SoloMedicos]
    http_method_names = ['get', 'post']

    def create(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        historia = serializer.save()

        # Generar PDF
        pdf_buffer = generar_pdf_historia_clinica(historia)

        # Crear carpeta media si no existe
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        # Ruta completa del archivo
        filename = f"historia_clinica_folio_{historia.Nro_folio}.pdf"
        pdf_path = os.path.join(settings.MEDIA_ROOT, filename)

        # Guardar PDF
        with open(pdf_path, "wb") as f:
            f.write(pdf_buffer.read())


        # Generar PDF de fórmulas médicas asociadas
        for formula in historia.formula_medica.all():
            print(f">>> Generando PDF fórmula {formula.id}...")
            pdf_buffer = generar_pdf_formula_medica(formula)
            formula_path = os.path.join(settings.MEDIA_ROOT, f"formula_medica_{formula.id}.pdf")
            with open(formula_path, "wb") as f:
                f.write(pdf_buffer.read())

        # Generar PDF de órdenes de procedimiento asociadas
        for orden in historia.orden_de_procedimientos.all():
            print(f">>> Generando PDF orden {orden.id}...")
            pdf_buffer = generar_pdf_orden_procedimiento(orden)
            orden_path = os.path.join(settings.MEDIA_ROOT, f"orden_procedimiento_{orden.id}.pdf")
            with open(orden_path, "wb") as f:
                f.write(pdf_buffer.read())


        return Response({
            'status': 'Historia clínica creada con éxito',
            'historia_clinica': self.get_serializer(historia).data,
            'pdf_historia_url': f"{settings.MEDIA_URL}{historia}",

            # Lista de URLs de las fórmulas médicas generadas
            'pdf_formulas_urls': [
                f"{settings.MEDIA_URL}formula_medica_{formula.id}.pdf"
                for formula in historia.formula_medica.all()
            ],

            
            'pdf_ordenes_urls': [
                f"{settings.MEDIA_URL}orden_procedimiento_{orden.id}.pdf"
                for orden in historia.orden_de_procedimientos.all()
            ]
        }, status=status.HTTP_201_CREATED)


    def get_queryset(self):
        queryset = super().get_queryset()
        nro_doc = self.request.query_params.get('nro_doc')
        year = self.request.query_params.get('year')

        # Buscar por documento del paciente
        if nro_doc:
            paciente = get_object_or_404(Paciente, usuario__nro_doc=nro_doc)
            queryset = queryset.filter(Nro_historia=paciente.usuario_id)

        # Filtrar por año si se solicita
        if year and year.isdigit():
            queryset = queryset.filter(fecha_atencion__year=int(year))

        return queryset

