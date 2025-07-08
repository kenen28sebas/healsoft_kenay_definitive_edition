from django.db import models
from datetime import datetime, timedelta


# Create your models here.

from django.db import models
from Usuarios.models import *
from django.utils.timezone import now

class HojaVida(models.Model):
    personal = models.ForeignKey(Usuario,on_delete=models.CASCADE)
    gestor_th = models.ForeignKey(Gestor_TH,on_delete=models.CASCADE)
    fecha_creacion=models.DateField(auto_now_add=True)


class Experiencia_laboral(models.Model):
    nombre_empresa=models.CharField(max_length=100,null=False, verbose_name='Nombre de la Empresa')
    cargo=models.CharField(max_length=100, null=False, verbose_name='Cargo')
    fecha_inicio=models.DateField(auto_now_add=False,auto_now=False, verbose_name='Fecha de Inicio')
    fecha_finalizacion=models.DateField(auto_now_add=False,auto_now=False, verbose_name='Fecha de Finalizacion')
    T_CONTRATO_CHOICES=[
        ("1","Contrato a término indefinido"),
        ("2","Contrato a término fijo"),
        ("3","Contrato por obra o labor"),
        ("4","Contrato ocasional, accidental o transitorio"),
        ("5","Contrato de aprendizaje"),
        ("6","Contrato de prestación de servicios"),
        ("7","Contrato sindical ")
    ]
    tipo_contrato=models.CharField(max_length=100, choices=T_CONTRATO_CHOICES,null=False,verbose_name="Tipo de contrato")
    soporte = models.FileField(upload_to='doc/')
    hoja_vida = models.ForeignKey(HojaVida,on_delete=models.CASCADE)

class Academico(models.Model):
    titulo_obtenido=models.CharField(max_length=100,null=False, verbose_name='Título Obtenido')
    institucion_educativa=models.CharField(max_length=100, null=False, verbose_name='Institución Educativa' )
    fecha_inicio=models.DateField(auto_now=False,auto_now_add=False, verbose_name='Fecha de Inicio')
    fecha_culminado=models.DateField(auto_now_add=False,auto_now=False, verbose_name='Fecha de Culminado')
    NIVEL_EDUCATIVO_CHOICES=[
        ("1",'Tecnico laboral en salud'),
        ("2",'Auxiliar de enfermeria'),
        ("3",'Auxiliar en salud oral'),
        ("4",'Auxiliar en servicios farmaceuticos'),
        ("5",'Auxiliar en atencion Prehospitalaria'),
        ("6",'Tecnologo en salud'),
        ("7",'Tecnologia en regencia de farmacia'),
        ("8",'Tecnologia en atenciaon prehospitalaria'),
        ("9",'Tecnologo en laboratorio clinico'),
        ("10",'medicina'),
        ("11",'enfermeria'),
        ("12",'odontologia'),
        ("13",'Fisioterapia'),
        ("14",'Terapia ocupacional'),
        ("15",'Bacteriologia y laboratorio clinico'),

    ]
    nivel_educativo=models.CharField(max_length=100,choices=NIVEL_EDUCATIVO_CHOICES, verbose_name='Nivel Educativo')
    soporte = models.FileField(upload_to='doc/')
    hoja_vida = models.ForeignKey(HojaVida,on_delete=models.CASCADE)



class SolicitudActualizacionHV(models.Model):
    ESTADO_SOLICITUD=[
        ('pendiente','Pendiente'),
        ('aprobada','Aprobada'),
        ('rechazada','Rechazada'),
    ]
    personal_medico=models.ForeignKey(Medico,on_delete=models.CASCADE)
    fecha_solicitud=models.DateField(auto_now_add=True)
    descripcion=models.TextField()
    estado=models.CharField(max_length=12,choices=ESTADO_SOLICITUD,default='pendiente')
    soporte = models.FileField(upload_to='doc/',default='')



class AgendaMes(models.Model):
    mes = models.DateField(auto_now_add=True)
    medico = models.ForeignKey(Medico , on_delete=models.CASCADE)
    publicado = models.BooleanField(default=False)


class AgendaDia(models.Model):
    dia = models.CharField(max_length=5,default="1")
    horainico = models.TimeField(auto_now=False,auto_now_add=False,blank=True,null=True)
    horafin = models.TimeField(auto_now=False,auto_now_add=False,blank=True,null=True)
    horaalmuerzo = models.TimeField(blank=True,null=True)
    agendames = models.ForeignKey(AgendaMes, on_delete=models.CASCADE,related_name='agendadia')