# Generated by Django 5.2.3 on 2025-07-09 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Gestion_citas', '0004_alter_cita_estado_alter_cita_tipo_atencion'),
    ]

    operations = [
        migrations.AddField(
            model_name='cita',
            name='hora_solicitud',
            field=models.TimeField(null=True),
        ),
        migrations.AlterField(
            model_name='cita',
            name='fecha_asignacion',
            field=models.DateField(unique=True),
        ),
    ]
