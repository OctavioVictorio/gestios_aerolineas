# Generated by Django 5.2.4 on 2025-07-05 00:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usuario',
            name='tipo_usuario',
        ),
        migrations.AddField(
            model_name='usuario',
            name='perfil',
            field=models.CharField(choices=[('cliente', 'Cliente'), ('empleado', 'Empleado'), ('admin', 'Administrador')], default='cliente', max_length=20),
        ),
    ]
