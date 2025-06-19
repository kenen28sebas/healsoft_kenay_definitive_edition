from django.db import models

from .manager import *

import datetime
from Usuarios.models import Usuario, Medico, Paciente
from Gerencia.models import Cups
from django.db import connection




# Create your models here.
# El CIE-10 es la Clasificación Internacional de Enfermedades 
class Cie10(models.Model):
    codigo_cie10 = models.CharField(verbose_name='Código de la enfermedad', max_length=20)
    nombre_cie10 = models.TextField(verbose_name='Nombre de la enfermedad')
    descripcion_cie10 = models.TextField(verbose_name='Descripción de la enfermedad')

    def __str__(self):
        return f"{self.codigo_cie10} - {self.nombre_cie10}"




class Anamnesis(models.Model):
    motivo_consulta = models.TextField(verbose_name='Motivo de la Consulta')
    sintomas = models.TextField(verbose_name='Síntomas')
    examen_fisico = models.TextField(verbose_name='Examen Físico')
    enfermedades_base = models.CharField(max_length=100, null=True, blank=True, verbose_name='Enfermedades de Base')
    SUSTANCIAS = [
        ('Seleccionar', 'Seleccionar'),
        ('Tabaco', 'Tabaco'),
        ('Alcohol', 'Alcohol'),
        ('Drogas', 'Drogas'),
        ('No', 'Ninguno')
    ]
    habitos = models.CharField(max_length=15, verbose_name='Consumo de sustancias', choices=SUSTANCIAS)
    ANTECEDENTES = [
        ("ninguno", "Ninguno"),
        ("familiar", "Familiar"),
        ("patologico", "Patológico"),
        ("no_patologico", "No Patológico"),
        ("alergico", "Alérgico"),
        ("quirurgico", "Quirúrgico"),
        ("farmacologico", "Farmacológico"),
        ("inmunologico", "Inmunológico"),
    ]
    antecedentes_medicos = models.CharField(max_length=15, verbose_name='Antecedentes médicos', choices=ANTECEDENTES)
    descripcion_antecedente = models.CharField(max_length=100, null=True, blank=True, verbose_name='Descripción del antecedente médico')

    def __str__(self):
        return f"Motivo: {self.motivo_consulta[:30]}"


class SignosVitales(models.Model):
    frecuencia_cardiaca = models.FloatField(verbose_name='Frecuencia Cardiaca')
    presion_arterial = models.FloatField(verbose_name='Presión Arterial')
    frecuencia_respiratoria = models.FloatField(verbose_name='Frecuencia Respiratoria')
    temperatura_corporal = models.FloatField(verbose_name='Temperatura Corporal')
    saturacion = models.IntegerField(verbose_name='Saturación')
    peso = models.FloatField(verbose_name='Peso')
    talla = models.FloatField(verbose_name='Talla')
    imc = models.FloatField(null=True, blank=True, verbose_name='Índice de Masa Corporal')

    def __str__(self):
        return f"Signos Vitales - PA: {self.presion_arterial}, FC: {self.frecuencia_cardiaca}"


class Paraclinicos(models.Model):
    resultados = models.TextField(null=True, blank=True, verbose_name='Resultados de los exámenes')
    analisis = models.TextField(null=True, blank=True, verbose_name='Análisis de los resultados')

    def __str__(self):
        return f"Paraclínicos - Análisis: {self.analisis[:30]}"



class Diagnostico(models.Model):
    ## Usar PROTECT evita que borres un código Cie10 o Cups si aún está en uso, lo cual mantiene la integridad y evita datos inconsistentes.
    cie10 = models.ForeignKey(Cie10, on_delete=models.PROTECT, verbose_name='Cie10')  
    TIPO_DIA = [
        ('Principal', 'Diagnóstico Principal'),
        ('Secundario', 'Diagnóstico secundario'),
        ('Diferencial', 'Diagnóstico Diferencial'),
        ('Confirmado', 'Diagnóstico Confirmado'),
        ('Presuntivo', 'Diagnóstico presuntivo'),
        ('Sindromico', 'Diagnóstico sindrómico'),
        ('Salud Mental', 'Diagnóstico de Salud Mental'),
        ('Preventivo', 'Diagnóstico Preventivo'),
        ('Riesgo', 'Diagnóstico de Riesgo'),
    ]
    tipo_diagnostico = models.CharField(max_length=20, verbose_name='Tipo de Diagnóstico', choices=TIPO_DIA)
    observaciones = models.CharField(max_length=200, null=True, blank=True, verbose_name='Observaciones')

    def __str__(self):
        return f"Diagnóstico: {self.cie10.nombre_cie10}, Tipo: ({self.tipo_diagnostico})"



class OrdenDeProcedimientos(models.Model):
    historia_clinica = models.ForeignKey('HistoriaClinica', on_delete=models.CASCADE, related_name="orden_de_procedimientos")
    codigo = models.IntegerField(unique=True, verbose_name='Código del procedimiento')
    cups = models.ForeignKey(Cups, on_delete=models.PROTECT)  # PROTECT para no borrar procedimientos usados
    cantidad = models.CharField(max_length=10, null=True, blank=True, verbose_name='Cantidad')
    descripcion = models.TextField(null=True)
    ESTADO_CHOICES = (
        ('RT', 'Rutinario'),
        ('UR', 'Urgente'),
        ('EM', 'Emergencia'),
        ('PD', 'Pendiente'),
        ('PG', 'Programado'),
        ('RA', 'Requiere Autorizacion'),
        ('NR', 'No Realizado'),
        ('SP', 'Suspendido'),
    )
    estado = models.CharField(max_length=2, verbose_name='Estado', choices=ESTADO_CHOICES)
    observacion = models.CharField(max_length=100, null=True, blank=True, verbose_name='Observación')

    def __str__(self):
        return f"Orden: {self.cups.nombre_cups} - Estado: {self.estado}"

    def save(self, *args, **kwargs):
        if not self.codigo:
            with connection.cursor() as cursor:
                cursor.execute("SELECT nextval('orden_procedimientos_codigo_seq')")
                self.codigo = cursor.fetchone()[0]
        super().save(*args, **kwargs)

####  Método save personalizado para asignar un código único automático.



class Medicamento(models.Model):
    formula_medica = models.ForeignKey('FormulaMedica', on_delete=models.CASCADE, related_name='medicamentos')
    nombre_medicamento = models.CharField(max_length=100, verbose_name='Nombre del Medicamento')
    concentracion = models.CharField(max_length=50, verbose_name='Concentracion del Medicamento')
    forma_farmaceutica = models.CharField(max_length=50, verbose_name='Forma Farmaceútica del Medicamento')
    dosis = models.CharField(max_length=50, verbose_name='Dosis')
    VIA_ADMIN_CHOICES = [
        ('VO', 'Vía oral'),
        ('VR', 'Vía rectal'),
        ('VT', 'Vía tópica'),
        ('TD', 'Vía transdérmica'),
        ('VI', 'Vía inhalatoria'),
        ('IV', 'Vía intravenosa'),
        ('IM', 'Vía intramuscular'),
        ('SC', 'Vía subcutánea'),
        ('IO', 'Vía intraósea'),
        ('IT', 'Vía intratecal'),
        ('SL', 'Vía sublingual')
    ]
    via_administracion = models.CharField(max_length=2, choices=VIA_ADMIN_CHOICES, verbose_name='Vía de Administración')
    frecuencia = models.CharField(max_length=20, verbose_name='Frecuencia del Medicamento')
    tiempo_tratamiento = models.CharField(max_length=30, verbose_name='Tiempo del Tratamiento')
    cantidad = models.CharField(max_length=10, verbose_name='Cantidad del Medicamento')
    cantidad_letras = models.CharField(max_length=50, verbose_name='Cantidad en letras')
    posologia = models.CharField(max_length=100, verbose_name='Posología')
    recomendaciones = models.CharField(max_length=100, null=True, blank=True, verbose_name='Recomendaciones')

    def __str__(self):
        return f"Medicamento: {self.nombre_medicamento} - {self.dosis}"




class FormulaMedica(models.Model):
    historia_clinica = models.ForeignKey('HistoriaClinica', on_delete=models.CASCADE, related_name='formula_medica')
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    diagnostico = models.ForeignKey(Diagnostico, on_delete=models.CASCADE)
    fecha_prescripcion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Fórmula: {self.medico.usuario.get_full_name()} - Diagnóstico: {self.diagnostico.cie10.codigo_cie10}"





class Evolucion(models.Model):
    historia_clinica = models.ForeignKey('HistoriaClinica', on_delete=models.CASCADE, related_name='evolucion')
    fecha_actual = models.DateField(auto_now_add=True)
    estado_paciente = models.TextField()
    diagnostico = models.ForeignKey(Diagnostico, on_delete=models.CASCADE)
    plan_de_manejo = models.TextField(verbose_name='Plan de Manejo')
    evolucion = models.TextField()
    recomendaciones = models.CharField(max_length=200, verbose_name='Recomendaciones')
    interconsultas = models.CharField(max_length=100, null=True, blank=True, verbose_name='Interconsultas')
    plan_de_seguimiento = models.CharField(max_length=200, null=True, blank=True, verbose_name='Plan de Seguimiento')
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)

    def __str__(self):
        return f"Evolución - {self.medico.usuario.get_full_name()} - {self.fecha_actual}"


class HistoriaClinica(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    anamnesis = models.OneToOneField(Anamnesis, on_delete=models.CASCADE)
    signos_vitales = models.OneToOneField(SignosVitales, on_delete=models.CASCADE)
    paraclinicos = models.OneToOneField(Paraclinicos, on_delete=models.CASCADE)
    diagnostico = models.ManyToManyField(Diagnostico, related_name='historias_clinicas')
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    Nro_historia = models.CharField(max_length=15, verbose_name='Numero de historia')
    fecha_atencion = models.DateTimeField(auto_now_add=True)
    Nro_folio = models.PositiveIntegerField(blank=True, null=True)

    objects = models.Manager()  # manager por defecto
    historia_manager = HistoriaManager()  # tu manager personalizado
    folio_manager = FolioManager()

    def save(self, *args, **kwargs):
        if not self.Nro_historia:
            self.Nro_historia = self.paciente.usuario.nro_doc
        if not self.Nro_folio:
            ultimo_folio = HistoriaClinica.objects.filter(paciente=self.paciente).count()
            self.Nro_folio = ultimo_folio + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Historia {self.Nro_historia} - Folio {self.Nro_folio}'

