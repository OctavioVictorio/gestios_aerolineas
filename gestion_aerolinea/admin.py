from django.contrib import admin
from .models import (
    Asiento, 
    Avion, 
    Boleto,
    Pasajero, 
    Reserva, 
    Vuelo, 
)

class AsientoInline(admin.TabularInline):
    model = Asiento
    extra = 0

@admin.register(Avion)
class AvionAdmin(admin.ModelAdmin):
    list_display = ('modelo', 'filas', 'columnas', 'capacidad')
    fields = ('modelo', 'filas', 'columnas', 'capacidad')
    readonly_fields = ('capacidad',)
    search_fields = ('modelo',)


@admin.register(Vuelo)
class VueloAdmin(admin.ModelAdmin):
    list_display = ('origen', 'destino', 'fecha_salida', 'fecha_llegada', 'estado', 'precio_base')
    list_filter = ('estado', 'origen', 'destino')
    search_fields = ('origen', 'destino')


@admin.register(Pasajero)
class PasajeroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'tipo_documento', 'numero_documento', 'email', 'telefono')
    search_fields = ('nombre', 'apellido', 'numero_documento', 'email')
    list_filter = ('tipo_documento',)


@admin.register(Asiento)
class AsientoAdmin(admin.ModelAdmin):
    list_display = ('avion', 'numero', 'fila', 'columna', 'tipo', 'estado')
    list_filter = ('tipo', 'estado', 'avion')
    search_fields = ('numero', 'avion_modelo')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('vuelo', 'pasajero', 'asiento', 'estado', 'fecha_reserva', 'precio_total', 'codigo_reserva')
    list_filter = ('estado', 'fecha_reserva')
    search_fields = ('codigo_reserva', 'pasajero__nombre', 'pasajero__apellido')


@admin.register(Boleto)
class BoletoAdmin(admin.ModelAdmin):
    list_display = ('reserva', 'codigo_barra', 'fecha_emision', 'estado')
    list_filter = ('estado',)
    search_fields = ('codigo_barra',)
