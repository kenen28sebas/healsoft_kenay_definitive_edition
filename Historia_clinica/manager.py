# en este archivo se van a encontrar los procedimientos que le corresponden a ala aplicacion Historia Clinica

from django.db import models
from Usuarios.models import Usuario, Paciente


class HistoriaManager(models.Manager):
    def listar_historia_documento(self, nro_doc):
        if not nro_doc:
            return self.none()  # Retorna un queryset vacío si nro_doc es None o incorrecto
        return self.filter(paciente__usuario__nro_doc=nro_doc).order_by('-fecha_atencion')


class FolioManager(models.Manager):
    def create_historia(self, paciente, medico, fecha_atencion):
        # Contar el número de historias previas del paciente
        ultimo_folio = self.filter(paciente=paciente).count()
        nuevo_folio = ultimo_folio + 1  # Incrementa el folio solo dentro del historial del paciente

        # Crear la historia con el nuevo folio
        historia = self.model(
            paciente=paciente,
            medico=medico,
            fecha_atencion=fecha_atencion,
            Nro_folio=nuevo_folio  # Aquí se asigna correctamente
        )
        historia.save(using=self._db)
        return historia