from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


# 👇 Manager personalizado para controlar la creación de usuarios y superusuarios
class UsuarioManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("El nombre de usuario es obligatorio")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """
        Crea un superusuario con permisos de administrador y perfil = 'admin'
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('perfil', 'admin')  # 👈 Se asegura que sea administrador

        if extra_fields.get('is_staff') is not True:
            raise ValueError("El superusuario debe tener is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("El superusuario debe tener is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)


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

    # 👇 Asociamos el manager personalizado
    objects = UsuarioManager()

    def __str__(self):
        return f"{self.username} ({self.get_perfil_display()})"
