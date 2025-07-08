from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, schema , authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
# from rest_framework.throttling import 
from .serializer import *
from Usuarios.models import Usuario
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import random

from rest_framework.permissions import BasePermission


from rest_framework.schemas import AutoSchema

@api_view(['POST'])
def registrar_gerente(request): 
    # Crear un nuevo gerente
    try:
        print("Validando contraseña del gerente")
        # Validar la contraseña 
        print("request.data:", request.data.get('usuario'))
        usuario = request.data.get('usuario')
        password = usuario["password"]
        validate_password(password=password)
    except Exception as e:
        # Si la validación falla, devolver un error
        return Response({"error": str(e)}, status=400)
    # Se crea el serializer correspondiente al tipo de usuario
    serializer=GerenteSerializador(data= request.data)
    if not serializer.is_valid():
        print("Errores de validación:", serializer.errors)
        return Response(serializer.errors, status=400)
    if serializer.is_valid(): 
        serializer.save()
        return Response({"message": "Usuario registrado exitosamente"}, status=201)
    else:
        print("Errores de validación:", serializer.errors)
        return Response(serializer.errors, status=400)

class CustomAutoSchema(AutoSchema):
    def get_link(self, path, method, base_url):
        link = super().get_link(path, method, base_url)
        if method == 'POST':
            link['description'] = 'Registrar un nuevo usuario'
        return link

@api_view(['POST'])
@schema(CustomAutoSchema())
def registrar_paciente(request):
    # Crear un nuevo paciente
    # Validar la contraseña
    try:
        usuario = request.data.get('usuario')
        password = usuario["password"]
        validate_password(password=password)
    except Exception as e:
        # Si la validación falla, devolver un error
        return Response({"error": str(e),"s":"s"}, status=400)
    if 'tipo_usuario' not in request.data or request.data['tipo_usuario'] != 'paciente':
        return Response({"error": "El campo 'tipo_usuario' debe ser 'paciente'"}, status=400)
    # Se crea el serializer correspondiente al tipo de usuario
    print("Datos del paciente:", request.data)
    serializer=PacienteSerializador(data= request.data)
    print(serializer.is_valid())
    if serializer.is_valid(): 
        print("Datos del paciente: 1", usuario)
        data_solicitud = {
            'usuario': usuario["nro_doc"],  # Obtener el número de documento del usuari
            'codigo_verificacion': generar_codigo_verificacion()  # Generar un código de verificación
        }
        solicitud_serializer = SolicitudContrasenaSerializador(data=data_solicitud)
        serializer.save()
        if not solicitud_serializer.is_valid():
            print("Errores de validación de solicitud:", solicitud_serializer.errors)
            return Response(solicitud_serializer.errors, status=400)
        solicitud_serializer.save()
        
        return Response({"message": "Usuario registrado exitosamente","codigo_verificacion" : data_solicitud["codigo_verificacion"]}, status=201)
    else:
        print("Errores de validación:", serializer.errors)
        return Response(serializer.errors, status=400)
    
@api_view(['POST'])
def registrar_roles(request):
    try:
        usuario = request.data
        password = usuario["password"]
        validate_password(password=password)
    except Exception as e:
        # Si la validación falla, devolver un error
        return Response({"error": str(e)}, status=400)

    # Se crea el serializer correspondiente al tipo de usuario    
    serializer = UsuarioSerializer(data=usuario)
    if serializer.is_valid(): 
        print("Datos del paciente: 1", usuario)
        data_solicitud = {
            'usuario': usuario["nro_doc"],  # Obtener el número de documento del usuari
            'codigo_verificacion': generar_codigo_verificacion()  # Generar un código de verificación
        }
        solicitud_serializer = SolicitudContrasenaSerializador(data=data_solicitud)
        print("Datos del paciente: 2", data_solicitud)
        serializer.save()
        if not solicitud_serializer.is_valid():
            print("Errores de validación de solicitud:", solicitud_serializer.errors)
            return Response(solicitud_serializer.errors, status=400)
        solicitud_serializer.save()
        
        return Response({"message": "Usuario registrado exitosamente","codigo_verificacion" : data_solicitud["codigo_verificacion"]}, status=201)
    else:
        print("Errores de validación:", serializer.errors)
        return Response(serializer.errors, status=400)

    
@api_view(['POST'])
@schema(CustomAutoSchema())
def activar_usuario(request):
    print("Activando usuario con datos:", request.data)
    nro_doc = request.data.get('nro_doc')
    print("Activando usuario con nro_doc:", nro_doc)
    if not nro_doc:
        return Response({"error": "El campo 'nro_doc' es obligatorio"}, status=400)
    # Activar un paciente
    try:
        codigo_verificacion = request.data.get('codigo_verificacion')
        codigo = Solicitud_contrasena.objects.filter(codigo_verificacion=codigo_verificacion).first()
        if not codigo:
            return Response({"error": "Código de verificación no existe"}, status=404)
        if codigo :
            if not codigo.estado:
                return Response({"error": "Código de verificación no válido o ya utilizado"}, status=400)
            
            usuario = get_object_or_404(Usuario, nro_doc=nro_doc)
            usuario.is_active = True  # Activar el usuario
            usuario.save()
            token, _ = Token.objects.get_or_create(user=usuario)
            codigo.estado = False  # Marcar el código como utilizado
            codigo.save()
            return Response({"message": "Usuario activado exitosamente", "token": token.key}, status=200)
    except Paciente.DoesNotExist:
        return Response({"error": "Paciente no encontrado"}, status=404)
        
    
@api_view(['POST'])
@schema(CustomAutoSchema())
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def actualizar_datos (request):
    datos_actualizar = request.data.get('datos_actualizar')
    print(datos_actualizar)
    datos_rol = request.data.get('datos_rol')
    if not datos_actualizar:
        return Response({"error": "El campo 'datos_actualizar' es obligatorio"}, status=400)
    tipo_usuario = request.data.get('tipo_usuario')
    try:
        usuario = Usuario.objects.get(nro_doc=request.data.get('nro_doc'))
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=404)    
    if not usuario.is_active:
        return Response({"error": "Usuario inactivo"}, status=403)
    if not tipo_usuario:
        return Response({"error": "El campo 'tipo_usuario' es obligatorio"}, status=400)
    if tipo_usuario not in ["medico", "gestor_th", "paciente", "auxiliar", "gerente"]:
        return Response({"error": "Tipo de usuario no válido"}, status=400)
    # Actualizar los datos de un usuario
    if not request.user.is_authenticated:
        return Response({"error": "Usuario no autenticado"}, status=401)
    # Se crea el serializer correspondiente al tipo de usuario

    serializer_usuario = UsuarioSerializer(usuario,data=datos_actualizar , partial=True)  # Permitir actualizaciones parciales
    if not serializer_usuario.is_valid():
        return Response(serializer_usuario.errors, status=400)      
    serializer_usuario.save()
    if tipo_usuario == "medico":
        try:
            datos_medico = {
                "especialidad": datos_rol.get("especialidad"),
                "contrato": datos_rol.get("contrato"),
                "usuario" :usuario.nro_doc
            }
            medico = Medico.objects.filter(usuario_id=usuario.nro_doc).first()
            if not medico:
                serializer_medico = MedicoSerializador(data = datos_medico)
                if not serializer_medico.is_valid():
                    return Response(serializer_medico.errors, status=400)
                if serializer_medico.is_valid():
                    serializer_medico.save(usuario=usuario)
                return  Response({"message": "Datos de usuario actualizados exitosamente"}, status=200)
            serializer_medico = MedicoSerializador(medico, data=datos_medico, partial=True)  # Permitir actualizaciones parciales
            if not serializer_medico.is_valid():
                return Response(serializer_medico.errors, status=400)
            serializer_medico.save()
            return Response({"message": "Datos de usuario actualizados exitosamente"}, status=200)
        except Medico.DoesNotExist:
            return Response({"error": "Médico no encontrado"}, status=404)
    if tipo_usuario == "gestor_th":
        try:
            datos_gestor_th = {
                "tipo_contrato": datos_rol.get("tipo_contrato"),
                "usuario": usuario.nro_doc
            }
            gestor_th = Gestor_TH.objects.filter(usuario_id=usuario.nro_doc).first()
            if not gestor_th:
                serializer_gestor_th = Gestor_thSerializador(data=datos_gestor_th)
                if not serializer_gestor_th.is_valid():
                    return Response(serializer_gestor_th.errors, status=400)
                if serializer_gestor_th.is_valid():
                    serializer_gestor_th.save(usuario=usuario)
                return Response({"message": "Datos de usuario actualizados exitosamente"}, status=200)
            serializer_gestor_th = Gestor_thSerializador(gestor_th, data=datos_gestor_th, partial=True)  # Permitir actualizaciones parciales
            if not serializer_gestor_th.is_valid():
                return Response(serializer_gestor_th.errors, status=400)
            if serializer_gestor_th.is_valid():
                serializer_gestor_th.save(usuario=usuario)
            return Response({"message": "Datos de usuario actualizados exitosamente"}, status=200)
        except Gestor_TH.DoesNotExist:
            return Response({"error": "Gestor TH no encontrado"}, status=404)  
    if tipo_usuario == "auxiliar":
        try:
            datos_aux = {
                "tipo_contrato": datos_rol.get("tipo_contrato"),
                "usuario": usuario.nro_doc
            }

            auxiliar = Aux_adm.objects.filter(usuario_id=usuario.nro_doc).first()

            if not auxiliar:
                serializer_aux = AuxiliarAdminSerializador(data=datos_aux)
                if not serializer_aux.is_valid():
                    return Response(serializer_aux.errors, status=400)
                serializer_aux.save(usuario=usuario)
                return Response({"message": "Datos de auxiliar creados exitosamente"}, status=200)

            serializer_aux = AuxiliarAdminSerializador(auxiliar, data=datos_aux, partial=True)
            if not serializer_aux.is_valid():
                return Response(serializer_aux.errors, status=400)
            serializer_aux.save(usuario=usuario)
            return Response({"message": "Datos de auxiliar actualizados exitosamente"}, status=200)

        except Aux_adm.DoesNotExist:
            return Response({"error": "Auxiliar administrativo no encontrado"}, status=404)
    
    if tipo_usuario == "paciente":
        try:
            datos_paciente = {
                "ocupacion": datos_rol.get("ocupacion"),
                "regimen": datos_rol.get("regimen"),  # 'RC', 'RS', 'RE' o 'PA'
                "eps": datos_rol.get("eps"),
                "estrato": datos_rol.get("estrato"),  # '1', '2', ..., '6'
                "grupo_atencion_especial": datos_rol.get("grupo_atencion_especial"),  # 'I', 'N', 'D' u 'O'
                "grupo_sanguineo": datos_rol.get("grupo_sanguineo"),
                "usuario": usuario.nro_doc
            }
            paciente = Paciente.objects.filter(usuario_id=usuario.nro_doc).first()
            if not paciente:
                serializer_paciente = PacienteSerializador(data=datos_paciente)
                if not serializer_paciente.is_valid():
                    return Response(serializer_paciente.errors, status=400)
                if serializer_paciente.is_valid():
                    serializer_paciente.save(usuario=usuario)
                return Response({"message": "Datos de usuario actualizados exitosamente"}, status=200)
            serializer_paciente = PacienteSerializador(paciente, data=datos_paciente, partial=True)  # Permitir actualizaciones parciales
            if not serializer_paciente.is_valid():
                return Response(serializer_paciente.errors, status=400)
            if serializer_paciente.is_valid():
                serializer_paciente.save(usuario=usuario)
            return Response({"message": "Datos de usuario actualizados exitosamente"}, status=200)
        except Paciente.DoesNotExist:
            return Response({"error": "Paciente no encontrado"}, status=404)  
    
    
    # print("Tipo de usuario:", tipo_usuario)
    # match tipo_usuario:
    #     case "medico":
    #         serializer=MedicoSerializador(data= request.data)
    #         if serializer.is_valid(): 
    #             serializer.save()
    #             return Response({"message": "Usuario registrado exitosamente"}, status=201)
    #         else:
    #             print("Errores de validación:", serializer.errors)
    #             return Response(serializer.errors, status=400)
    #     case "paciente":
    #         serializer=PacienteSerializador(data= request.data)
    #         if serializer.is_valid(): 
    #             serializer.save()
    #             return Response({"message": "Usuario registrado exitosamente"}, status=201)
    #         else:
    #             print("Errores de validación:", serializer.errors)
    #             return Response(serializer.errors, status=400)
    #     case "auxiliar":
    #         serializer=AuxiliarAdminSerializador(data= request.data)
    #         if serializer.is_valid(): 
    #             serializer.save()
    #             return Response({"message": "Usuario registrado exitosamente"}, status=201)
    #         else:
    #             print("Errores de validación:", serializer.errors)
    #             return Response(serializer.errors, status=400)  
    #     case "gestor_th":
    #         serializer=Gestor_thSerializador(data= request.data)
    #         if serializer.is_valid(): 
    #             serializer.save()
    #             return Response({"message": "Usuario registrado exitosamente"}, status=201)
    #         else:
    #             print("Errores de validación:", serializer.errors)
    #             return Response(serializer.errors, status=400)  
    #     case "gerente":
    #         serializer=GerenteSerializador(data= request.data)
    #         if serializer.is_valid(): 
    #             serializer.save()
    #             return Response({"message": "Usuario registrado exitosamente"}, status=201)
    #         else:
    #             print("Errores de validación:", serializer.errors)
    #             return Response(serializer.errors, status=400)
    
@api_view(['POST'])
def login(request):  
    # Iniciar sesión de un usuario
    print("Iniciando sesión con datos:", request.data)
    try:
        nro_doc = request.data.get('nro_doc') 
        user = Usuario.objects.get(nro_doc=nro_doc)
        password = request.data.get('password')
        user.check_password(password)  # Verifica la contraseña
        if not user.check_password(password):
            return Response({"error": "Contraseña incorrecta"}, status=400)
        if not user.is_active:
            return Response({"error": "Usuario inactivo"}, status=403)
        Token.objects.filter(user=user).delete()  # Elimina el token anterior si existe
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=404)
    
    token, _ = Token.objects.get_or_create(user=user)
    paciente = Paciente.objects.filter(usuario_id=nro_doc).first()
    if paciente:
        datos_paciente = PacienteSerializador(instance=paciente)
        print("Datos del paciente:", datos_paciente.data)
        return Response({"user": datos_paciente.data, "token": token.key,"tipo_usuario" : "paciente"}, status=200)
    medico = Medico.objects.filter(usuario_id=nro_doc).first()
    if medico:
        datos_medico = MedicoSerializador(instance=medico)
        print("Datos del médico:", datos_medico.data)
        return Response({"user": datos_medico.data, "token": token.key,"tipo_usuario" : "medico"}, status=200)
    gestor_th = Gestor_TH.objects.filter(usuario_id=nro_doc).first()
    if gestor_th:
        datos_gestor_th = Gestor_thSerializador(instance=gestor_th)
        print("Datos del gestor TH:", datos_gestor_th.data)
        return Response({"user": datos_gestor_th.data, "token": token.key,"tipo_usuario" : "gestor_th"}, status=200)
    auxiliar = Aux_adm.objects.filter(usuario_id=nro_doc).first()
    if auxiliar:
        datos_auxiliar = AuxiliarAdminSerializador(instance=auxiliar)
        print("Datos del auxiliar administrativo:", datos_auxiliar.data)
        return Response({"user": datos_auxiliar.data, "token": token.key,"tipo_usuario" : "auxiliar"}, status=200)
    gerente = Gerente.objects.filter(usuario_id=nro_doc).first()
    if gerente:
        datos_gerente = GerenteSerializador(instance=gerente)
        print("Datos del gerente:", datos_gerente.data)
        return Response({"user": datos_gerente.data, "token": token.key,"tipo_usuario" : "gerente"}, status=200)   

    
    datos_usuario = UsuarioSerializer(instance=user)
    print("Datos del usuario:", datos_usuario.data)
    return Response({"user": datos_usuario.data, "token": token.key}, status=200)
# El código anterior se ha comentado porque no es necesario para el funcionamiento actual.
    



# @api_view(['POST'])
# def login(request):
#     # Iniciar sesión de un usuario
#     if 'tipo_usuario' not in request.data:
#         return Response({"error": "El campo 'tipo_usuario' es obligatorio"}, status=400)
#     tipo_usuario = request.data["tipo_usuario"]
#     if tipo_usuario not in ["medico", "gestor_th", "paciente", "auxiliar", "gerente"]:
#         return Response({"error": "Tipo de usuario no válido"}, status=400)
#     try:
#         nro_doc = request.data.get('nro_doc') 
#         user = Usuario.objects.get(nro_doc=nro_doc)
#         password = request.data.get('password')
#         user.check_password(password)  # Verifica la contraseña
#         if not user.check_password(password):
#             return Response({"error": "Contraseña incorrecta"}, status=400)
#         if not user.is_active:
#             return Response({"error": "Usuario inactivo"}, status=403)
#         Token.objects.filter(user=user).delete()  # Elimina el token anterior si existe
#     except Usuario.DoesNotExist:
#         return Response({"error": "Usuario no encontrado"}, status=404)
    
#     match tipo_usuario:
#         case "medico":
#             try:
#                 medico = get_object_or_404(Medico, usuario_id=request.data["nro_doc"])
#                 token, _ = Token.objects.get_or_create(user=user)
#                 datos_medico = MedicoSerializador(instance=medico)
#                 return Response({"user": datos_medico.data, "token": token.key, "tipo de usuario": "medico"}, status=200)
#             except Medico.DoesNotExist:
#                 return Response({"error": "Médico no encontrado"}, status=404)

#         case "gestor_th":
#             try:
#                 gestor_th = get_object_or_404(Gestor_TH, usuario_id=request.data["nro_doc"])
#                 token, _ = Token.objects.get_or_create(user=user)
#                 datos_gestor_th = Gestor_thSerializador(instance=gestor_th)
#                 return Response({"user": datos_gestor_th.data, "token": token.key, "tipo de usuario": "gestor_th"}, status=200)
#             except Gestor_TH.DoesNotExist:
#                 return Response({"error": "Gestor TH no encontrado"}, status=404)

#         case "paciente":
#             try:
#                 paciente = get_object_or_404(Paciente, usuario_id=request.data["nro_doc"])
#                 token, _ = Token.objects.get_or_create(user=user)
#                 datos_paciente = PacienteSerializador(instance=paciente)
#                 return Response({"user": datos_paciente.data, "token": token.key, "tipo de usuario": "paciente"}, status=200)
#             except Paciente.DoesNotExist:
#                 return Response({"error": "Paciente no encontrado"}, status=404)

#         case "auxiliar":
#             try:
#                 auxiliar = get_object_or_404(Aux_adm, usuario_id=request.data["nro_doc"])
#                 token, _ = Token.objects.get_or_create(user=user)
#                 datos_auxiliar = AuxiliarAdminSerializador(instance=auxiliar)
#                 return Response({"user": datos_auxiliar.data, "token": token.key, "tipo de usuario": "auxiliar"}, status=200)
#             except Aux_adm.DoesNotExist:
#                 return Response({"error": "Auxiliar administrativo no encontrado"}, status=404)

#         case "gerente":
#             try:
#                 gerente = get_object_or_404(Gerente, usuario_id=request.data["nro_doc"])
#                 token, _ = Token.objects.get_or_create(user=user)
#                 datos_gerente = GerenteSerializador(instance=gerente)
#                 return Response({"user": datos_gerente.data, "token": token.key, "tipo de usuario": "gerente"}, status=200)
#             except Gerente.DoesNotExist:
#                 return Response({"error": "Gerente no encontrado"}, status=404)

      
#     return Response({"message": "Inicio de sesión exitoso"}, status=200)
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    # Cerrar sesión de un usuario
    if request.user.is_authenticated:
        Token.objects.filter(user=request.user).delete()  # Elimina el token del usuario
        return Response({"message": "Sesión cerrada exitosamente"}, status=200)
    else:
        return Response({"error": "Usuario no autenticado"}, status=401)

@api_view(['post'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def cambiar_contrasena(request):
    print(request.data.get('restaurar'))
    if not request.data.get('restaurar'):
        if not request.user.is_authenticated:
            return Response({"error": "Usuario no autenticado"}, status=401)
        password = request.data.get('password')
        request.user.check_password(password)  # Verifica la contraseña actual
        if not request.user.check_password(password):
            return Response({"error": "Contraseña incorrecta"}, status=400)
    # Cambiar la contraseña de un usuario
   
    try:
        usuario = Usuario.objects.get(nro_doc=request.user.nro_doc)
        nueva_contrasena = request.data.get('nueva_contrasena')
        if not nueva_contrasena:
            return Response({"error": "El campo 'nueva_contrasena' es obligatorio"}, status=400)
        
        validate_password(password=nueva_contrasena, user=usuario)  # Validar la nueva contraseña
        usuario.set_password(nueva_contrasena)  # Establecer la nueva contraseña
        usuario.save()  # Guardar el usuario
        return Response({"message": "Contraseña cambiada exitosamente"}, status=200)
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=400)

def generar_codigo_verificacion():
    # Generar un código de verificación aleatorio
    return str(random.randint(100000, 999999))  # Código de 6 dígitos

@api_view(['POST'])
def solicitar_restaurar_contrasena(request):
    # Solicitar restauración de contraseña
    try:
        nro_doc = request.data.get('nro_doc')
        if not nro_doc:
            return Response({"error": "El campo 'nro_doc' es obligatorio"}, status=400)
        usuario = get_object_or_404(Usuario,nro_doc=nro_doc)
        print(usuario.nro_doc)
        if not usuario.is_active:
            return Response({"error": "Usuario inactivo"}, status=403)
        # Generar un código de verificación
        codigo_verificacion = generar_codigo_verificacion()
        data = {
            'usuario': usuario.nro_doc,
            'codigo_verificacion': codigo_verificacion # Aquí se podría establecer una fecha de expiración
        }
        serializer = SolicitudContrasenaSerializador(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        if serializer.is_valid():
            serializer.save()
        # Guardar la solicitud de restauración de contraseña
        return Response({"message": "Solicitud de restauración de contraseña enviada","email":usuario.email}, status=200)
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=404)
# Create your views here.

@api_view(['POST'])
def restaurar_contrasena(request):
    print("Datos recibidos:", request.data)
    try:
        codigo_verificacion = request.data.get('codigo_verificacion')
        codigo = Solicitud_contrasena.objects.get(codigo_verificacion=codigo_verificacion)
        usuario = get_object_or_404(Usuario, nro_doc=codigo.usuario_id)
        token, _ = Token.objects.get_or_create(user=usuario) 
        # Crear o obtener el token del usuario
        if not codigo.estado:
            return Response({"error": "Código de verificación no válido o ya utilizado"}, status=400)
        codigo.estado = False
        print("Código de verificación:", codigo_verificacion)
        codigo.save()  # Marcar el código como utilizado
        return Response({"message": "Código de verificación válido","contrasena":usuario.password,"token":token.key}, status=200)
    except Solicitud_contrasena.DoesNotExist:
        return Response({"error": "Solicitud de restauración de contraseña no encontrada"}, status=404) 
    
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def actualizar_datos_usuario(request):
    # Actualizar los datos de un usuario
    if not request.user.is_authenticated:
        return Response({"error": "Usuario no autenticado"}, status=401)
    
    try:
        usuario = Usuario.objects.get(nro_doc=request.user.nro_doc)
        serializer = UsuarioSerializer(usuario, data=request.data, partial=True)  # Permitir actualizaciones parciales
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Datos de usuario actualizados exitosamente"}, status=200)
        else:
            return Response(serializer.errors, status=400)
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=404)    

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def lista_medicos(request):     
    medicos = Medico.objects.all()
    serializer = MedicoSerializador(medicos, many=True)
    return Response(serializer.data)