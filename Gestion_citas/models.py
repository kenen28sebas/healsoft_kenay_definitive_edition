from django.db import models
from Gerencia.models import Centro_medico, Servicio
from Usuarios.models import Paciente, Medico



class Cita(models.Model):
    fecha_asignacion = models.DateField()
    fecha_solicitud = models.DateField(auto_now=True)
    estado = models.CharField(max_length=20, choices=[
        ('Pendiente', 'Pendiente'),
        ('Confirmada', 'Confirmada'),
        ('Cancelada', 'Cancelada'),
        ('Atendida', 'Atendida')
    ])
    especialidad = models.CharField(max_length=100)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    tipo_atencion = models.CharField(max_length=50, choices=[
        ('Presencial', 'Presencial'),
        ('Virtual', 'Virtual'),
    ])
    centro_medico = models.ForeignKey(Centro_medico, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    

    def __str__(self):
        return f"{self.paciente} - {self.fecha} {self.hora}"
    
class Info_cambio(models.Model):
    fecha_cambio = models.DateField()
    tipo_cambio = models.CharField(max_length=50)
    observacion = models.CharField(max_length=255)
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.cita} - {self.fecha_cambio} {self.hora_cambio}"
    
    