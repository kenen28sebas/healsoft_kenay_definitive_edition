from rest_framework import serializers
from Gestion_TH.models import *


class HojaVidaSerializer(serializers.ModelSerializer):
    class Meta:
            model=HojaVida
            fields = [
                "id",
                "personal_medico",
                "gestor_th",
                "fecha_creacion"
            ]

class ExperienciaSerializer(serializers.ModelSerializer):

    fecha_inicio = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y", "%Y-%m-%d"])
    fecha_finalizacion = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y", "%Y-%m-%d"])

    class Meta:
        model = Experiencia_laboral
        fields = [
            "id",
            "nombre_empresa",
            "cargo",
            "fecha_inicio",
            "fecha_finalizacion",
            "tipo_contrato",
            "hoja_vida",
            "soporte"
        ]

class AcademicoSerializer(serializers.ModelSerializer):
    fecha_inicio = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y", "%Y-%m-%d"])
    fecha_culminado = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y", "%Y-%m-%d"])
    class Meta:
        model = Academico
        fields = [
            "id",
            "titulo_obtenido",
            "institucion_educativa",
            "fecha_inicio",
            "fecha_culminado",
            "nivel_educativo",
            "hoja_vida",
            "soporte",
        ]


class SolicitudSerializer(serializers.ModelSerializer):

    class Meta:
        model = SolicitudActualizacionHV
        fields =[
            "personal_medico",
            "fecha_solicitud",
            "descripcion",
            "estado",
        ]


class AgendaDiaSerializer(serializers.ModelSerializer):
    trabajado = serializers.SerializerMethodField()
    bloques = serializers.SerializerMethodField()

    class Meta:
        model = AgendaDia
        fields = ['id', 'horainico', 'horafin', 'trabajado', 'bloques']

    def get_trabajado(self, obj):
        return obj.horainico is not None

    def get_bloques(self, obj):
        if not obj.horainico or not obj.horafin:
            return []

        # Obtener la duración de la cita desde el médico
        agenda_mes = obj.agendames
        medico = agenda_mes.medico
        duraciones = {
            "Medicina General": 20,
            "Odontología": 30,
            "Laboratorios": 20
        }
        duracion = duraciones.get(medico.especialidad, 20)

        # Convertir horas a datetime para poder operar
        bloques = []
        hora_actual = datetime.combine(datetime.today(), obj.horainico)
        hora_fin = datetime.combine(datetime.today(), obj.horafin)

        # Recuperar hora de almuerzo desde la agenda
        hora_almuerzo = getattr(obj, 'horaalmuerzo', None)
        if hora_almuerzo:
            hora_almuerzo = datetime.combine(datetime.today(), hora_almuerzo)

        while hora_actual < hora_fin:
            siguiente_bloque = hora_actual + timedelta(minutes=duracion)

            # Saltar el bloque si es hora de almuerzo
            if hora_almuerzo and hora_actual.time() == hora_almuerzo.time():
                hora_actual = siguiente_bloque
                continue

            bloques.append(f"{hora_actual.strftime('%H:%M')} - {siguiente_bloque.strftime('%H:%M')}")
            hora_actual = siguiente_bloque

        return bloques

class AgendaMesSerializer(serializers.ModelSerializer):
    agendadia = AgendaDiaSerializer(many=True, read_only=True)

    class Meta:
        model = AgendaMes
        fields = ['id', 'mes', 'publicado', 'agendadia']
