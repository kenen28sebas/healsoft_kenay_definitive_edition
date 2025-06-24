import datetime
from rest_framework import serializers
from Usuarios.models import *
from rest_framework.authtoken.models import Token

class UsuarioSerializer (serializers.ModelSerializer):
    fecha_exp_doc = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y", "%Y-%m-%d"] ,required=False)
    fecha_nacimiento = serializers.DateField(format="%d/%m/%Y", input_formats=["%d/%m/%Y", "%Y-%m-%d"],required=False)
    email = serializers.EmailField(required=True, allow_blank=False)

    class Meta :
        model = Usuario
        fields =[
            "nro_doc", 
            "tipo_doc",
            "lugar_exp_doc",
            "fecha_exp_doc",
            "sexo" ,
            "fecha_nacimiento" ,
            "estado_civil" ,
            "telefono", 
            "nacionalidad", 
            "municipio" ,
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "is_active",
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')  # Se extrae la contraseña
        usuario = Usuario.objects.create(**validated_data)
        usuario.set_password(password) 
        token, created = Token.objects.get_or_create(user=usuario)
        usuario.save()
        return usuario 
    
class MedicoSerializador(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True) 
    class Meta : 
        model = Medico
        fields = "__all__"
    
    def create(self, validated_data):
        usuario_data = validated_data.pop('usuario') 
        usuario_exist = Usuario.objects.filter(
            nro_doc=usuario_data.nro_doc,
        ).first()
        token, created = Token.objects.get_or_create(user=usuario_exist)  #crear token para el usuario
        medico = Medico.objects.create(usuario=usuario_exist, **validated_data)  # Crea el médico
        return medico
    
class Gestor_thSerializador(serializers.ModelSerializer):
    usuario=UsuarioSerializer(read_only = True)

    class Meta:
        model=Gestor_TH
        fields="__all__"

    def create(self, validated_data):
        usuario_data = validated_data.pop('usuario') 
        usuario_exist = Usuario.objects.filter(
            nro_doc=usuario_data.nro_doc,
        ).first()
        token, created = Token.objects.get_or_create(user=usuario_exist) #crear token para el usuario
        gestor_th=Gestor_TH.objects.create(usuario=usuario_exist, **validated_data)
        return gestor_th
    
class PacienteSerializador(serializers.ModelSerializer):
    usuario = UsuarioSerializer()

    class Meta:
        model = Paciente
        fields = "__all__"

    def create(self, validated_data):
        print("Datos del paciente: 1", validated_data)
        usuario_data = validated_data.pop('usuario')
        print("sdasd",usuario_data)
        usuario_exist = Usuario.objects.filter(
            nro_doc=usuario_data['nro_doc'],
        ).first()
        if not usuario_exist:
            usuario=UsuarioSerializer.create(UsuarioSerializer(),validated_data=usuario_data)
            token, created = Token.objects.get_or_create(user=usuario)
            paciente = Paciente.objects.create(usuario=usuario, **validated_data)  # Crear el paciente
            return paciente
        token, created = Token.objects.get_or_create(user=usuario_exist)  # Crear token para el usuario
        paciente = Paciente.objects.create(usuario=usuario_exist, **validated_data)  # Crear el paciente
        return paciente

class AuxiliarAdminSerializador(serializers.ModelSerializer):
    usuario = UsuarioSerializer()
    class Meta:
        model = Aux_adm
        fields="__all__"

    def create(self, validated_data):
        usuario_data=validated_data.pop('usuario')
        usuario=UsuarioSerializer.create(UsuarioSerializer(),validated_data=usuario_data)
        token, created = Token.objects.get_or_create(user=usuario)  #crear token para el usuario
        aux_adm = Aux_adm.objects.create(usuario = usuario, **validated_data )
        return aux_adm
    
class GerenteSerializador(serializers.ModelSerializer):
    usuario = UsuarioSerializer()
    class Meta:
        model=Gerente
        fields="__all__"

    def create(self, validated_data):
        usuario_data=validated_data.pop('usuario')
        usuario=UsuarioSerializer.create(UsuarioSerializer(),validated_data=usuario_data)
        token,created=Token.objects.get_or_create(user=usuario)
        gerente = Gerente.objects.create(usuario = usuario, **validated_data)
        return gerente
class SolicitudContrasenaSerializador(serializers.ModelSerializer):
    class Meta:
        model = Solicitud_contrasena
        fields = [
            'usuario',
            'codigo_verificacion',
        ]

    def create(self, validated_data):
        usuario_data = validated_data.pop('usuario')
        print(usuario_data)  # Obtiene el usuario basado en los datos proporcionados
        fecha_solicitud = datetime.datetime.now()
        fecha_expiracion = fecha_solicitud + datetime.timedelta(minutes=5)  # Expira en 5 minutos
        solicitud_contrasena = Solicitud_contrasena.objects.create(usuario=usuario_data,**validated_data,fecha_expiracion=fecha_expiracion, fecha_solicitud=fecha_solicitud , estado=True)
    
        print(solicitud_contrasena)
        solicitud_contrasena.save()
        return solicitud_contrasena