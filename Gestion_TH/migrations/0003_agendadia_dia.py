# Generated by Django 5.2.3 on 2025-07-05 04:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Gestion_TH', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='agendadia',
            name='dia',
            field=models.CharField(default='1', max_length=5),
        ),
    ]
