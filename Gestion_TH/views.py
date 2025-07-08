from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from Usuarios.models import *
from Usuarios.serializer import *
from .serializer import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, schema , authentication_classes, permission_classes
from datetime import datetime, date, timedelta
from rest_framework.views import APIView
from holidays import country_holidays
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.response import Response
from Gerencia.models import *
from Usuarios.models import Gerente, Gestor_TH, Medico
from Usuarios.serializer import MedicoSerializador 





class Gerentevistas(viewsets.ViewSet):

    def ver_cups(self, request):
        usuario = request.user
        gerente = Gerente.objects.filter(usuario__nro_doc= usuario.nro_doc).first()

        if not gerente:
            return Response({"error":"No estas autorizado para consultar los cups :)"})
        
        cups = Cups.objects.all()

        # serializer = CupsSerializer(cups , many = True)

        # return Response(serializer.data , status=status.HTTP_200_OK)
    
#esta clase me ayuda a manejar los permisos para que solo el gestor de talento humano pueda hacer uso de los end points
#lo que hago es definir una clase de permisos personalizados haciendo uso de IsAuthenticated lo que quiere decir que solo los usuaris registrados podrian hacer solicitudes
class EsGestorth(IsAuthenticated):
#este metodo lo uso para saber si el usuario tiene permiso para realizar la accion en la vista
    def has_permission(self, request, view):
#aqui estoy verificando si el usuario registrado es un gestor de talento humano
        return Gestor_TH.objects.filter(usuario=request.user).exists()
    
class EsMedico(IsAuthenticated):

     def has_permission(self, request, view):
          return Medico.objects.filter(usuario=request.user).exists()

#esta vista me permite registrar medicos y asociarle su hoja de vida en el momento que se crea el registro
class HojaVistas(viewsets.ModelViewSet):
#aqui estoy configurando la vista para trabajar con el modelo medico
    queryset = Medico.objects.all()
#hacemos uso del serializador para convertir los datos a json
    serializer_class = MedicoSerializador
    authentication_classes =[TokenAuthentication]
#aqui estoy definiendo los permisos para hacer uso de la vista, haciendo uso del IsAuthenticated y de EsGestorth que es el que verifica que sea un gestor de th
    permission_classes = [IsAuthenticated,EsGestorth]  
#con este metodo registro medicos y automaticamente genero su hoja de vida

    def create(self, request, *args, **kwargs):
        print("Datos recibidos:", request.user)  # Debugging line to check incoming data
        gestor = Gestor_TH.objects.filter(usuario=request.user).first()
        if not gestor:
                return Response({"error": "Solo el Gestor de Talento Humano puede registrar médicos."}, status=status.HTTP_403_FORBIDDEN)

        usuario_data = request.data.pop("usuario", None)
        usuario_data = usuario_data.pop("usuario", None)
        print(usuario_data)
        if not usuario_data:
                return Response({"error": "Los datos del usuario son requeridos."}, status=status.HTTP_400_BAD_REQUEST)

        #Validar si el cargo existe y está habilitado antes de asignarlo
        # cargo_id = request.data.pop("cargo", None)  #Eliminamos cargo de request.data
        # try:
        #         cargo = Cargo.objects.get(id=cargo_id)
        #         if not cargo.estado:
        #                 return Response({"error": "El cargo seleccionado está inhabilitado."}, status=status.HTTP_400_BAD_REQUEST)
        # except Cargo.DoesNotExist:
        #         return Response({"error": "El cargo no existe."}, status=status.HTTP_404_NOT_FOUND)

        # usuario_instance = Usuario.objects.create(**usuario_data)
        # usuario_instance.set_password(usuario_data["password"])
        # usuario_instance.save()

        #Eliminamos cargo de request.data antes de crear Medico
        # medico_instance = Medico.objects.create(usuario=usuario_instance, cargo=cargo, **request.data)
        medico = Medico.objects.filter(usuario__nro_doc=usuario_data["nro_doc"]).first()
        usuario = Usuario.objects.filter(nro_doc=usuario_data["nro_doc"]).first()
        print(medico.usuario_id)
        hoja_vida_instance = HojaVida.objects.create(
                personal=usuario,
                gestor_th=gestor
        )

        return Response({
                "mensaje": "Médico y hoja de vida registrados con éxito.",
                "medico": MedicoSerializador(medico).data,
                "hoja_vida": HojaVidaSerializer(hoja_vida_instance).data
        }, status=status.HTTP_201_CREATED)
    

#definimos un metodo list que usaremos para obtener la lista de todos los medicos
    def list(self, request, *args, **kwargs):
#verificamos que el usuario autenticado sea un gestor de talento humano 
        gestor = Gestor_TH.objects.filter(usuario=request.user).first()
#si no es un gestor de talento humano le mostramos un mensaje 
        if not gestor:
            return Response({"error": "Solo el gestor de talento humano puede ver la lista de médicos"}, status=status.HTTP_403_FORBIDDEN)

#aqui obtenemos todos los registros del modelo medico y select_related nos ayuda a obtener los datos del usuario relacionado
        medicos = Medico.objects.select_related("usuario").all()
#luego convertimos la lista de los medicos obtenidos a formato json (many=true indica que estamos serializando varios regsitros)
        serializer = MedicoSerializador(medicos, many=True)
#el metodo nos devuelve un mensaje con la lista de los medicos registrados y un status 200
        return Response({
            "mensaje": "Lista de médicos obtenida con éxito",
            "medicos": serializer.data
        }, status=status.HTTP_200_OK)

#con este metodo vamos a eliminar a el medico a el usuario y la hoja de vida, con pk=none estamos recibiendo el atributo unico del usuario (nro_doc)
    def destroy(self, request, pk=None):
#aqui verificamos si el usuario autenticado es un gestor de talento humano
        gestor = Gestor_TH.objects.filter(usuario=request.user).first()
#si no es un gestor se le avisa que no tiene permisos para eliminar personal medico
        if not gestor:
            return Response({"mensaje": "No tienes permiso para eliminar registros"}, status=status.HTTP_403_FORBIDDEN)
#buscamoes en la tabla del usuario el numero de documento que figura como la llave primaria
        usuario = Usuario.objects.filter(nro_doc=pk).first()
#si el usuario no se encuentra se muestra el error 404
        if not usuario:
            return Response({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)
#aqui buscamos en la tabla medico el registro asociado a el numero de documento
        medico = Medico.objects.filter(usuario=usuario).first()
#si el usuario dado no es un medico entonces se mostrara el error 404
        if not medico:
            return Response({"error": "Médico no encontrado para este usuario"}, status=status.HTTP_404_NOT_FOUND)
#aqui buscamos en la hoja de vida el registro vinculado a ese medico y lo eliminamos 
        HojaVida.objects.filter(personal_medico=medico).delete()
#eliminamos el registro del medico
        medico.delete()
#y finalmete eliminamis el registro del usuario
        usuario.delete()
#el endpoint responde con un mensaje de exito
        return Response({"mensaje": "Médico eliminado correctamente"}, status=status.HTTP_200_OK)


#con este metodo vamos a actualizar el registro del medico    
    def update(self, request, pk=None, **kwargs):
#verificamos que el usuario autenticado es un gestor de th
        gestor = Gestor_TH.objects.filter(usuario=request.user).first()
#si no le enviamos un mensaje de error 
        if not gestor:
                return Response({"mensaje": "No tienes permiso para actualizar registros"}, status=status.HTTP_403_FORBIDDEN)
#aqui buscamos en la tabla usuario el registro por su nro_doc (llave primaria de la tabla)
        usuario = Usuario.objects.filter(nro_doc=pk).first()  
#si el usuario es none enviamos un error 404
        if not usuario:
                return Response({"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

#buscamos en la tabla medico el registro encontrado en la tabla usuario
        medico = Medico.objects.filter(usuario=usuario).first()
#si ese usuario no es un medico enviamos un error 404
        if not medico:
                return Response({"error": "Médico no encontrado para este usuario"}, status=status.HTTP_404_NOT_FOUND)
#aqui extraemos los datos enviados en la solicitud, si no enviamis nada extraemos un {} diccionario vacio
        usuario_data = request.data.get("usuario", {})  
#iteramos sobre los campos que enviamos para actualizarlos
        for key, value in usuario_data.items(): 
#asignamos el valor a cada uno de los campos 
                setattr(usuario, key, value)
#guardamos el registro del usuario actualizado
        usuario.save() 
#aqui extraemos los datos enviados en la solicitud, si no enviamis nada extraemos un {} diccionario vacio
        medico_data = request.data.get("medico", {})
#iteramos sobre los campos que enviamos para actualizarlos
        for key, value in medico_data.items():
#asignamos el valor a cada uno de los campos 
                setattr(medico, key, value)
#se guarda el registro actualizado
        medico.save()
        return Response({"mensaje": "Médico y usuario actualizados correctamente"}, status=status.HTTP_200_OK)



class AcademicoVistas(viewsets.ModelViewSet):
     queryset = Academico.objects.all()
     serializer_class = AcademicoSerializer
     permission_classes = [IsAuthenticated, EsGestorth]  

     def create(self, request, *args, **kwargs):
        gestor = Gestor_TH.objects.filter(usuario=request.user).first()
        if not gestor:
                return Response({"error": "No tienes permiso para registrar información académica"}, status=status.HTTP_403_FORBIDDEN)
        print(request.POST.get("nro_doc"))
        nro_doc = request.POST.get("nro_doc")
        usuario = Usuario.objects.filter(nro_doc=nro_doc).first()
        if not usuario:
                return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        id_personal = ""
        medico = Medico.objects.filter(usuario=usuario).first()

        if medico:
            id_personal = medico.usuario_id
            print("Es médico:", id_personal)
        else:
            auxiliar = Aux_adm.objects.filter(usuario__nro_doc=nro_doc).first()
            if auxiliar:
                id_personal = auxiliar.usuario_id
                print("Es auxiliar:", id_personal)
            else:
                return Response({"error": "El usuario no está registrado como médico ni como auxiliar."}, status=status.HTTP_404_NOT_FOUND)



        hoja_vida = HojaVida.objects.filter(personal=id_personal).first()
        print(3)
        if not hoja_vida:
                return Response({"error": "El médico no tiene una hoja de vida"}, status=status.HTTP_404_NOT_FOUND)

        print(1)
        titulo_obtenido = request.POST.get("titulo_obtenido")
        institucion_educativa = request.POST.get("institucion_educativa")
        fecha_inicio = request.POST.get("fecha_inicio")
        fecha_culminado = request.POST.get("fecha_culminado")
        nivel_educativo = request.POST.get("nivel_educativo")
        soporte_pdf = request.FILES.get("soporte")


        required_fields = [titulo_obtenido, institucion_educativa, fecha_inicio, fecha_culminado, nivel_educativo]
        if None in required_fields:
                return Response({"error": "Todos los campos son obligatorios"}, status=status.HTTP_400_BAD_REQUEST)
        # print(f"Archivo recibido: {request.FILES.get('soporte')}")
        # print(f"Debug - Archivos recibidos: {request.FILES}")
        # print(f"Debug - Archivo 'soporte': {request.FILES.get('soporte')}")

        academico = Academico.objects.create(
                hoja_vida=hoja_vida,
                titulo_obtenido=titulo_obtenido,
                institucion_educativa=institucion_educativa,
                fecha_inicio=fecha_inicio,
                fecha_culminado=fecha_culminado,
                nivel_educativo=nivel_educativo,
                soporte=soporte_pdf
        )

        return Response({"mensaje": "El académico fue creado correctamente"}, status=status.HTTP_201_CREATED)
     
     def list(self, request, *args, **kwargs):
        #Verificar que el usuario sea un gestor de talento humano
        gestor = Gestor_TH.objects.filter(usuario=request.user).first()
        if not gestor:
            return Response({"error": "No tienes permiso para usar esta vista"}, status=status.HTTP_403_FORBIDDEN)

        #Obtener `nro_doc` de los parámetros de la solicitud
        nro_doc = request.query_params.get("nro_doc")

        if not nro_doc:
            return Response({"error": "Debes proporcionar el número de documento"}, status=status.HTTP_400_BAD_REQUEST)

        #Buscar usuario, médico y hoja de vida en una sola consulta
        Usuario.objects.filter(nro_doc__exact="6").exists()
        usuario = get_object_or_404(Usuario, nro_doc=nro_doc)
        medico = get_object_or_404(Medico, usuario=usuario)
        hoja_vida = get_object_or_404(HojaVida, personal_medico=medico)

        #Obtener académicos asociados a la hoja de vida
        academicos = Academico.objects.filter(hoja_vida=hoja_vida)
        serializer = AcademicoSerializer(academicos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
     
     def update(self, request,pk=None):
        # Verificar que el usuario sea un gestor de talento humano
        gestor = Gestor_TH.objects.filter(usuario=request.user).first()
        if not gestor:
            return Response({"error": "No tienes permiso para actualizar registros."}, status=status.HTTP_403_FORBIDDEN)

        # Obtener el `nro_doc` de la solicitud
        nro_doc = request.query_params.get("nro_doc")
        if not nro_doc:
            return Response({"error": "Debes proporcionar el número de documento del médico."}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar el médico con ese `nro_doc`
        usuario = get_object_or_404(Usuario, nro_doc=nro_doc)
        medico = get_object_or_404(Medico, usuario=usuario)
        hoja_vida = get_object_or_404(HojaVida, personal_medico=medico)

        # Obtener el académico asociado a esa hoja de vida
        academico = get_object_or_404(Academico, hoja_vida=hoja_vida, pk=pk)

        #Validar y actualizar los datos
        serializer = AcademicoSerializer(academico, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

     def destroy(self, request, pk=None):
        #Verificar que el usuario sea un gestor de talento humano
        gestor = Gestor_TH.objects.filter(usuario=request.user).first()
        if not gestor:
            return Response({"error": "No tienes permiso para eliminar registros."}, status=status.HTTP_403_FORBIDDEN)

        # Obtener el `nro_doc` de la solicitud
        nro_doc = request.query_params.get("nro_doc")
        if not nro_doc:
            return Response({"error": "Debes proporcionar el número de documento del médico."}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar el médico con ese `nro_doc`
        usuario = get_object_or_404(Usuario, nro_doc=nro_doc)
        medico = get_object_or_404(Medico, usuario=usuario)
        hoja_vida = get_object_or_404(HojaVida, personal_medico=medico)

        #Obtener el académico asociado a esa hoja de vida
        academico = get_object_or_404(Academico, hoja_vida=hoja_vida, pk=pk)

        #Eliminar el registro
        academico.delete()

        return Response({"mensaje": "Académico eliminado correctamente."}, status=status.HTTP_200_OK)
     


class ExperienciVistas(viewsets.ModelViewSet):
    queryset = Experiencia_laboral.objects.all()  # ✅ Corregir el queryset
    serializer_class = ExperienciaSerializer
    permission_classes = [IsAuthenticated, EsGestorth]

    def create(self, request, *args, **kwargs):
        gestor = Gestor_TH.objects.filter(usuario=request.user).first()
        if not gestor:
            return Response({"error": "Solo el gestor de talento humano tiene acceso a esta vista"}, status=status.HTTP_403_FORBIDDEN)

        nro_doc = request.POST.get("nro_doc")
        if not nro_doc:
            return Response({"error": "Debes proporcionar el número de documento del usuario"}, status=status.HTTP_400_BAD_REQUEST)

        usuario = Usuario.objects.filter(nro_doc=nro_doc).first()
        if not usuario:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        personal_id = None
        medico = Medico.objects.filter(usuario=usuario).first()
        if medico:
            personal = medico.usuario_id
        else:
            auxiliar = Aux_adm.objects.filter(usuario=usuario).first()
            if auxiliar:
                personal = auxiliar.usuario_id
            else:
                return Response({"error": "El usuario no está registrado como médico ni como auxiliar."}, status=status.HTTP_404_NOT_FOUND)

        hoja_vida = HojaVida.objects.filter(personal=personal).first()
        if not hoja_vida:
            return Response({"error": "El usuario no tiene una hoja de vida registrada"}, status=status.HTTP_404_NOT_FOUND)

        # Extraer campos de experiencia laboral
        nombre_empresa = request.POST.get("nombre_empresa")
        cargo = request.POST.get("cargo")
        fecha_inicio = request.POST.get("fecha_inicio")
        fecha_finalizacion = request.POST.get("fecha_finalizacion")
        tipo_contrato = request.POST.get("tipo_contrato")
        soporte_pdf = request.FILES.get("soporte")

        campos_requeridos = [nombre_empresa, cargo, fecha_inicio, fecha_finalizacion, tipo_contrato]
        if None in campos_requeridos:
            return Response({"error": "Todos los campos son obligatorios para registrar experiencia"}, status=status.HTTP_400_BAD_REQUEST)

        experiencia = Experiencia_laboral.objects.create(
            hoja_vida=hoja_vida,
            nombre_empresa=nombre_empresa,
            cargo=cargo,
            fecha_inicio=fecha_inicio,
            fecha_finalizacion=fecha_finalizacion,
            tipo_contrato=tipo_contrato,
            soporte=soporte_pdf
        )

        return Response({"mensaje": "La experiencia laboral fue registrada correctamente"}, status=status.HTTP_201_CREATED)

    
    def list(self, request, *args, **kwargs):
        #Verificar que el usuario sea un gestor de talento humano
        gestor = Gestor_TH.objects.filter(usuario=request.user).first()
        if not gestor:
            return Response({"error": "No tienes permiso para acceder a esta información."}, status=status.HTTP_403_FORBIDDEN)

        # Obtener `nro_doc` de los parámetros de la solicitud
        nro_doc = request.query_params.get("nro_doc")
        if not nro_doc:
            return Response({"error": "Debes proporcionar el número de documento del médico."}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar el médico con ese `nro_doc`
        usuario = get_object_or_404(Usuario, nro_doc=nro_doc)
        medico = get_object_or_404(Medico, usuario=usuario)
        hoja_vida = get_object_or_404(HojaVida, personal_medico=medico)

        #Obtener todas las experiencias asociadas a esa hoja de vida
        experiencias = Experiencia_laboral.objects.filter(hoja_vida=hoja_vida)
        serializer = ExperienciaSerializer(experiencias, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, pk=None):
        #Verificar que el usuario sea un gestor de talento humano
        gestor = Gestor_TH.objects.filter(usuario=request.user).first()
        if not gestor:
            return Response({"error": "No tienes permiso para actualizar registros."}, status=status.HTTP_403_FORBIDDEN)

        #Obtener `nro_doc` de la solicitud
        nro_doc = request.query_params.get("nro_doc")
        if not nro_doc:
            return Response({"error": "Debes proporcionar el número de documento del médico."}, status=status.HTTP_400_BAD_REQUEST)

        #Buscar el médico con ese `nro_doc`
        usuario = get_object_or_404(Usuario, nro_doc=nro_doc)
        medico = get_object_or_404(Medico, usuario=usuario)
        hoja_vida = get_object_or_404(HojaVida, personal_medico=medico)

        #Obtener la experiencia laboral asociada a esa hoja de vida
        experiencia = get_object_or_404(Experiencia_laboral, hoja_vida=hoja_vida, pk=pk)

        #Validar y actualizar los datos
        serializer = ExperienciaSerializer(experiencia, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
    def destroy(self, request, pk=None):
        #Verificar que el usuario sea un gestor de talento humano
        gestor = Gestor_TH.objects.filter(usuario=request.user).first()
        if not gestor:
            return Response({"error": "No tienes permiso para eliminar registros."}, status=status.HTTP_403_FORBIDDEN)

        #Obtener `nro_doc` de la solicitud
        nro_doc = request.query_params.get("nro_doc")
        if not nro_doc:
            return Response({"error": "Debes proporcionar el número de documento del médico."}, status=status.HTTP_400_BAD_REQUEST)

        #Buscar el médico con ese `nro_doc`
        usuario = get_object_or_404(Usuario, nro_doc=nro_doc)
        medico = get_object_or_404(Medico, usuario=usuario)
        hoja_vida = get_object_or_404(HojaVida, personal_medico=medico)

        #Obtener la experiencia laboral asociada a esa hoja de vida
        experiencia = get_object_or_404(Experiencia_laboral, hoja_vida=hoja_vida, pk=pk)

        #Eliminar el registro
        experiencia.delete()

        return Response({"mensaje": "Experiencia laboral eliminada correctamente."}, status=status.HTTP_200_OK)


class SolicitudActualizacionVistas(viewsets.ModelViewSet):
    serializer_class = SolicitudSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        #Verificar que el usuario logueado sea un médico
        medico = Medico.objects.filter(usuario=request.user).first()
        if not medico:
                return Response({"error": "Solo médicos pueden registrar solicitudes."}, status=status.HTTP_403_FORBIDDEN)

        #Obtener datos de la solicitud
        descripcion = request.data.get("descripcion")
        soporte_pdf = request.FILES.get("soporte")

        #Guardar la solicitud en la base de datos
        solicitud = SolicitudActualizacionHV.objects.create(
                personal_medico=medico,
                descripcion=descripcion,
                soporte=soporte_pdf,
        )

        return Response({"mensaje": "Solicitud registrada correctamente."}, status=status.HTTP_201_CREATED)
    def list(self, request, *args, **kwargs):
        #Verificar que el usuario logueado sea un médico
        medico = Medico.objects.filter(usuario=request.user).first()
        if not medico:
                return Response(
                        {"error": "Solo médicos pueden ver sus solicitudes."},
                        status=status.HTTP_403_FORBIDDEN
                )

        #Filtrar las solicitudes de ese médico
        solicitudes = SolicitudActualizacionHV.objects.filter(personal_medico=medico)
        serializer = self.get_serializer(solicitudes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def update(self, request, *args, **kwargs):
        medico = Medico.objects.filter(usuario=request.user).first()
        if not medico:
            return Response(
                {"error": "Solo médicos pueden actualizar sus solicitudes."},
                status=status.HTTP_403_FORBIDDEN
            )

        solicitud_id = kwargs.get("pk")
        solicitud = SolicitudActualizacionHV.objects.filter(id=solicitud_id, personal_medico=medico).first()
        if not solicitud:
            return Response(
                {"error": "No puedes actualizar esta solicitud o no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        #Obtener el nuevo archivo si se envía en la solicitud
        nuevo_soporte = request.FILES.get("soporte")
        if nuevo_soporte:
            solicitud.soporte = nuevo_soporte  #Actualizar archivo de soporte

        #Aplicar la actualización con los datos enviados
        serializer = self.get_serializer(solicitud, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
    def destroy(self, request, *args, **kwargs):
        medico = Medico.objects.filter(usuario=request.user).first()
        if not medico:
            return Response(
                {"error": "Solo médicos pueden eliminar sus solicitudes."},
                status=status.HTTP_403_FORBIDDEN
            )

        solicitud_id = kwargs.get("pk")
        solicitud = SolicitudActualizacionHV.objects.filter(id=solicitud_id, personal_medico=medico).first()
        if not solicitud:
            return Response(
                {"error": "No puedes eliminar esta solicitud o no existe."},
                status=status.HTTP_404_NOT_FOUND
            )

        solicitud.delete()#Eliminar la solicitud
        return Response({"mensaje": "Solicitud eliminada correctamente."}, status=status.HTTP_204_NO_CONTENT)



class EsGerente(IsAuthenticated):
#este metodo lo uso para saber si el usuario tiene permiso para realizar la accion en la vista
    def has_permission(self, request, view):
#aqui estoy verificando si el usuario registrado es un gerente
        return Gerente.objects.filter(usuario=request.user).exists()
    
# class CargoVistas(viewsets.ModelViewSet):
#      serializer_class=CargoSerilizer
#      permission_classes=[IsAuthenticated,EsGerente]

#      def create(self, request, *args, **kwargs):
#           gerente = Gerente.objects.filter(usuario=request.user).first()
#           if not gerente:
#                return Response({"error":"Solo el gerente puede registrar cargos"},status=status.HTTP_403_FORBIDDEN)
          
#           return super().create(request, *args, **kwargs)
     
#      def list(self, request, *args, **kwargs):
#         cargos = Cargo.objects.all()

#         if not cargos.exists():
#             return Response({"mensaje": "No hay cargos registrados en el sistema."}, status=status.HTTP_404_NOT_FOUND)

#         serializer = CargoSerilizer(cargos, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
     
#      def update(self, request, pk=None, *args, **kwargs):
#         try:
#             cargo = Cargo.objects.get(id=pk)
#         except Cargo.DoesNotExist:
#             return Response({"error": "El cargo no existe."}, status=status.HTTP_404_NOT_FOUND)

#         serializer = CargoSerilizer(cargo, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         #Validación: Si el cargo está inhabilitado, no se podrá asignar a médicos
#         if not serializer.validated_data.get("estado", cargo.estado):
#             Medico.objects.filter(cargo=cargo).update(cargo=None)

#         return Response({"mensaje": "Cargo actualizado correctamente.", "cargo": serializer.data})
     

#      def destroy(self, request, pk=None, *args, **kwargs):
#         try:
#             cargo = Cargo.objects.get(id=pk)
#         except Cargo.DoesNotExist:
#             return Response({"error": "El cargo no existe."}, status=status.HTTP_404_NOT_FOUND)

#         #Validación: Si el cargo está asignado a médicos, primero se desvincula
#         Medico.objects.filter(cargo=cargo).update(cargo=None)
#         cargo.delete()
#         return Response({"mensaje": "Cargo eliminado correctamente."}, status=status.HTTP_204_NO_CONTENT)




class AgendaMesViewSet(viewsets.ModelViewSet):
    queryset = AgendaMes.objects.prefetch_related('agendadia').all()
    serializer_class = AgendaMesSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        print(request.data)
        try:
            nro_doc = request.data.get("nro_doc")
            mes_raw = request.data.get("mes")  # Esperado: "2025-08" o "2025-08-01"

            if not nro_doc or not mes_raw:
                return Response({"error": "Faltan datos obligatorios: 'nro_doc' o 'mes'."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Buscar el médico
            medico = Medico.objects.filter(usuario__nro_doc=nro_doc).first()
            if not medico:
                return Response({"error": "No se encontró el médico con ese número de documento."},
                                status=status.HTTP_404_NOT_FOUND)

            # Formatear fecha a un objeto datetime.date
            try:
                fecha_mes = datetime.strptime(mes_raw[:10], "%Y-%m-%d").date()
            except ValueError:
                try:
                    fecha_mes = datetime.strptime(mes_raw[:7], "%Y-%m").date()
                except ValueError:
                    return Response({"error": "Formato de fecha inválido. Usa 'YYYY-MM' o 'YYYY-MM-DD'."},
                                    status=status.HTTP_400_BAD_REQUEST)

            # Construir los datos
            data = {
                "medico": medico.id,
                "mes": fecha_mes,
                "publicado": True
            }

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Ocurrió un error inesperado: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AgendaDiaViewSet(viewsets.ModelViewSet):
    queryset = AgendaDia.objects.all()
    serializer_class = AgendaDiaSerializer
    # permission_classes = [permissions.IsAuthenticated]        

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def buscar_usuario_por_documento(request):
    nro_doc = request.query_params.get('nro_doc')
    if not nro_doc:
        return Response({'error': 'Número de documento no proporcionado'}, status=400)

    usuario = Usuario.objects.filter(nro_doc=nro_doc).first()
    if not usuario:
        return Response({'existe': False}, status=404)

    serializer = UsuarioSerializer(usuario)
    return Response({'existe': True, 'usuario': serializer.data}, status=200)
#esta vista me permite registrar medicos y asociarle su hoja de vida en el momento que se crea el registro
# class HojaVistas(viewsets.ModelViewSet):
# #aqui estoy configurando la vista para trabajar con el modelo medico
#     queryset = Medico.objects.all()
# #hacemos uso del serializador para convertir los datos a json
#     serializer_class = MedicoSerializador
#     authentication_classes =[TokenAuthentication]
# #aqui estoy definiendo los permisos para hacer uso de la vista, haciendo uso del IsAuthenticated y de EsGestorth que es el que verifica que sea un gestor de th
#     permission_classes = [IsAuthenticated,EsGestorth]  
# #con este metodo registro medicos y automaticamente genero su hoja de vida