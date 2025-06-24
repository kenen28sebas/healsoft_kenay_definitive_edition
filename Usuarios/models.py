from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario (AbstractUser):
    nro_doc = models.CharField(max_length=12,primary_key=True,null=False)
    tdoc = [
        ('CC', 'cedula de ciudadania'),
        ('CE', 'cedula de Extranjeria'),
        ('TI', 'Tarjeta de identidad'), 
        ('RC', 'Registro civil'),
        ('PA', 'Pasaporte'),
        ('ASI', 'Adulto sin identificaion'),
        ('MSI', 'Menor sin identificaion'),
    ]
    tipo_doc = models.CharField(max_length=3,null=False, choices=tdoc)
    lugar_exp_doc = models.CharField(max_length=50,null=True)
    fecha_exp_doc = models.DateField(null=True) 
    sex = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('I','Indeterminado')
    ]
    sexo = models.CharField(max_length=1,null=True,choices=sex)
    fecha_nacimiento = models.DateField( null=True)
    ec = [
        ('Soltero','Soltero'),
        ('Casado','Casado'),
        ('Divorciado','Divorciado'),
        ('Viudo','Viudo'),
        ('Union Libre','Union Libre'),
        ('Separado','Separado'),
    ]
    estado_civil = models.CharField(max_length=15,null=True,choices=ec)
    telefono = models.CharField(max_length=15,null=True)
    nacionalidad = models.CharField(max_length=30,null=True)
    municipio = models.CharField( max_length=50,null=True)

class Medico(models.Model):
    EPECIALIDADES_CHOICES=[ 
        ('Pediatría', 'Pediatría'),
        ('Medicina General', 'Medicina General'),
        ('Enfermería', 'Enfermería'),
    ]
    especialidad = models.CharField(max_length=100, choices=EPECIALIDADES_CHOICES, null=False, verbose_name='Especialidad')
    TP_CONTRATO_CHOICES=[
        ("1","Contrato a término indefinido"),
        ("2","Contrato a término fijo"),
        ("3","Contrato por obra o labor"),
        ("4","Contrato ocasional, accidental o transitorio"),
        ("5","Contrato de aprendizaje"),
        ("6","Contrato de prestación de servicios"),
        ("7","Contrato sindical ")
    ]
    contrato=models.CharField(choices=TP_CONTRATO_CHOICES, null=False,verbose_name='Contarto', max_length=50)
    usuario=models.ForeignKey(Usuario,on_delete=models.CASCADE)
    CARGO_CHOICES=[
        ('auxiliar', 'auxiliar'),
        ('jefe', 'jefe')
    ]
class Gestor_TH(models.Model):
    T_CONTRATO_CHOICES=[
        ('1',"Contrato a término indefinido"),
        ('2',"Contrato a término fijo"),
        ('3',"Contrato por obra o labor"),
        ('4',"Contrato ocasional, accidental o transitorio"),
        ('5',"Contrato de aprendizaje"),
        ('6',"Contrato de prestación de servicios"),
        ('7',"Contrato sindical ")
    ]
    tipo_contrato=models.CharField(max_length=100, choices=T_CONTRATO_CHOICES,null=False,verbose_name="Tipo de contrato" , default="hola")
    usuario=models.ForeignKey(Usuario,on_delete=models.CASCADE)


class Paciente(models.Model):
    ocupacion = models.CharField(max_length=100, null=True, blank=False, verbose_name='Ocupacion')
    REG = [
        ('RC', 'Régimen Contributivo'),
        ('RS', 'Régimen Subsidiado'),
        ('RE', 'Régimen Especial'),
        ('PA', 'Particular')
    ]
    regimen = models.CharField(max_length=10, null=True, blank=False, choices=REG )
    eps = models.CharField(max_length=100, null=True, blank=False, verbose_name='EPS')
    ES = [
        ('1', 'Estrato 1'),
        ('2', 'Estrato 2'),
        ('3', 'Estrato 3'),
        ('4', 'Estrato 4'),
        ('5', 'Estrato 5'),
        ('6', 'Estrato 6')
    ]
    estrato = models.CharField(max_length=1, null=True, blank=False, verbose_name='Estrato', choices=ES)
    # TIPO_A = [
    #     ('COT', 'Cotizante'),
    #     ('BEN', 'Beneficiario'),
    #     ('ADI', 'Adicional'),
    #     ('NC', 'No Cotizante')
    # ]
    # tipo_afiliacion = models.CharField(max_length=3, null=False, blank=False, verbose_name='Tipo de Afiliación', choices=TIPO_A)
    GRUPO_A_E = [
        ('I', 'Indígena'),
        ('N', 'Negro'),
        ('D', 'Desplazado'),
        ('O', 'Otro')
    ]
    grupo_atencion_especial = models.CharField(max_length=1, null=True, blank=False, verbose_name='Grupo de Atención Especial', choices=GRUPO_A_E)
    GRPO_SANG = [
        ('A+', 'A Positivo'),
        ('A-', 'A Negativo'),
        ('B+', 'B Positivo'),
        ('B-', 'B Negativo'),
        ('AB+', 'AB Positivo'),
        ('AB-', 'AB Negativo'),
        ('O+', 'O Positivo'),
        ('O-', 'O Negativo')
    ]
    grupo_sanguineo = models.CharField(max_length=3, null= True, blank= False, verbose_name='RH', choices=GRPO_SANG)
    usuario=models.ForeignKey(Usuario,on_delete=models.CASCADE)
    
# class Gerente(models.Model) :
#     pass   
       
class Aux_adm(models.Model) :
    T_CONTRATO_CHOICES=[
        ('1',"Contrato a término indefinido"),
        ('2',"Contrato a término fijo"),
        ('3',"Contrato por obra o labor"),
        ('4',"Contrato ocasional, accidental o transitorio"),
        ('5',"Contrato de aprendizaje"),
        ('6',"Contrato de prestación de servicios"),
        ('7',"Contrato sindical ")
    ]
    tipo_contrato=models.CharField(max_length=100, choices=T_CONTRATO_CHOICES,null=False,verbose_name="Tipo de contrato" , default="hola")
    usuario=models.ForeignKey(Usuario,on_delete=models.CASCADE)

class Gerente(models.Model):
    usuario=models.ForeignKey(Usuario,on_delete=models.CASCADE)
    profesion=models.CharField(max_length=100)
    T_CONTRATO_CHOICES=[
        ('1',"Contrato a término indefinido"),
        ('2',"Contrato a término fijo"),
        ('3',"Contrato por obra o labor"),
        ('4',"Contrato ocasional, accidental o transitorio"),
        ('5',"Contrato de aprendizaje"),
        ('6',"Contrato de prestación de servicios"),
        ('7',"Contrato sindical ")
    ]
    tipo_contrato=models.CharField(max_length=100, choices=T_CONTRATO_CHOICES,null=False,verbose_name="Tipo de contrato" , default="hola")


class Solicitud_contrasena(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField()
    codigo_verificacion = models.CharField(max_length=50, null=False, blank=False)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f'Solicitud de contraseña para {self.usuario.username} - Estado: {"Activa" if self.estado else "Inactiva"}'    