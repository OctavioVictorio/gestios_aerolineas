from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {'fields': ('perfil',)}),
    )
    list_display = ('username', 'email', 'perfil', 'is_staff', 'is_superuser')

admin.site.register(Usuario, UsuarioAdmin)
