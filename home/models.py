from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    PERFILES = [
        ('cliente', 'Cliente'),
        ('empleado', 'Empleado'),
        ('admin', 'Administrador'),
    ]

    perfil = models.CharField(
        max_length=20,
        choices=PERFILES,
        default='cliente',
    )

    def __str__(self):
        return f"{self.username} ({self.get_perfil_display()})"
