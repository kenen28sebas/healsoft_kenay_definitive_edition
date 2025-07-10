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


from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from datetime import datetime
from .models import Servicio
from Gestion_citas.models import Cita
from Usuarios.models import Medico,Paciente,Usuario




@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def dashboard_admin(request):
    # 🗓 Citas por mes
    citas_por_mes = Cita.objects.annotate(
        mes=models.functions.TruncMonth('fecha_asignacion')
    ).values('mes').annotate(total=Count('id')).order_by('mes')

    citas_por_mes_data = {
        dato['mes'].strftime('%Y-%m'): dato['total'] for dato in citas_por_mes
    }

    # 🩺 Servicios activos vs inactivos
    servicios_activos = Servicio.objects.filter(estado=True).count()
    servicios_inactivos = Servicio.objects.filter(estado=False).count()

    # 🧑‍⚕️ Top 5 médicos por cantidad de citas
    top_medicos_raw = Cita.objects.values('medico').annotate(total=Count('id')).order_by('-total')[:5]
    top_medicos = []
    for item in top_medicos_raw:
        try:
            medico = Medico.objects.get(id=item['medico'])
            nombre = f"{medico.usuario.first_name} {medico.usuario.last_name}"
        except:
            nombre = "—"
        top_medicos.append({
            "medico": nombre,
            "citas": item['total']
        })

    # 👥 Usuarios por rol
    usuarios_por_rol = {
    "paciente": Paciente.objects.count(),
    "medico": Medico.objects.count(),
    "aux_adm": Aux_adm.objects.count(),
    "gerente": Gerente.objects.count(),
    "gestor_th": Gestor_TH.objects.count()
}
    # 🧾 Régimen y EPS más frecuentes
    regimen_frecuente_raw = Paciente.objects.values('regimen').annotate(total=Count('id')).order_by('-total')
    regimen_frecuente = {r['regimen']: r['total'] for r in regimen_frecuente_raw}

    eps_frecuentes_raw = Paciente.objects.values('eps').annotate(total=Count('id')).order_by('-total')
    eps_frecuentes = {e['eps']: e['total'] for e in eps_frecuentes_raw}

    # ❌ Estado de citas
    estado_citas_raw = Cita.objects.values('estado').annotate(total=Count('id'))
    estado_citas = {c['estado']: c['total'] for c in estado_citas_raw}

    # 📦 Respuesta final
    data = {
        "citas_por_mes": citas_por_mes_data,
        "servicios_activos": servicios_activos,
        "servicios_inactivos": servicios_inactivos,
        "top_medicos": top_medicos,
        "usuarios_por_rol": usuarios_por_rol,
        "regimen_frecuente": regimen_frecuente,
        "eps_frecuentes": eps_frecuentes,
        "estado_citas": estado_citas,
    }

    return Response(data)
