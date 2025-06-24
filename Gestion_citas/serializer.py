from rest_framework import serializers
from .models import Cita,Info_cambio

class CitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cita
        fields = '__all__'

class InfoCambioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Info_cambio
        fields = '__all__'
        