from rest_framework import serializers
from .models import Cita,Info_cambio
from Usuarios.serializer import PacienteSerializador , MedicoSerializador
from Gerencia.serializer import Centro_medicoSerializer,ServicioSerializer

class CitaSerializer(serializers.ModelSerializer):
    # paciente = PacienteSerializador(read_only = True)
    
    fecha_asignacion = serializers.DateTimeField(
    format='%d-%m-%Y %H:%M:%S',
    input_formats=[
        '%Y-%m-%dT%H:%M:%S.%fZ',  # <-- ISO 8601 con milisegundos y zona Z
        '%d-%m-%Y %H:%M:%S',
        '%d-%m-%Y',
        '%Y/%m/%d'
    ]
)


    class Meta:
        model = Cita
        fields = ['fecha_asignacion','estado','especialidad','servicio','tipo_atencion','centro_medico','medico','paciente']

class InfoCambioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Info_cambio
        fields = '__all__'
        