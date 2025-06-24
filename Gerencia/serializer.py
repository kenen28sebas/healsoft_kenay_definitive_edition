from  rest_framework import serializers
from .models import Centro_medico, Servicio, Cups

class CupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cups
        fields = ['codigo', 'nombre', 'servicio', 'estado']

class Centro_medicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Centro_medico
        fields = ['nit','nombre', 'direccion', 'telefono', 'email']

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = "__all__"