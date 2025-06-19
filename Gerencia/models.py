from django.db import models

# Create your models here.
class Centro_medico(models.Model):
    nit = models.CharField(max_length=20, unique=True, primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nombre
    

class Servicio(models.Model):
    capitulo = models.CharField(max_length=10, unique=True,primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    estado = models.BooleanField(default=False)
    

    def __str__(self):
        return self.nombre    
    
class Cups(models.Model):
    codigo = models.CharField(max_length=10, unique=True,primary_key=True)
    nombre = models.CharField(max_length=800, unique=True)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    estado = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre    