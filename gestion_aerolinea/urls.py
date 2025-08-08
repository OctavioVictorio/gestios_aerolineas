from django.urls import path
from .views import (
    CancelarReservaView,
    CancelarReservaEmpleadoView,
    ConfirmarReservaView,
    CrearVueloView,
    DetallesVueloView,
    EditarPasajeroView,
    EditarVueloView,      
    EliminarPasajeroView,
    EliminarVueloView,    
    GestionarPasajerosView,
    GestionarReservasEmpleadoView,
    GestionarVuelosView,
    PanelClienteView,
    PanelEmpleadoView,
    SeleccionarAsientoView,
    VerReservasClienteView,
    VerVuelosClienteView
)

urlpatterns = [
    # Rutas para clientes 
    path('cliente/', PanelClienteView.as_view(), name='panel_cliente'),
    
    # Rutas para Clientes (vuelos)
    path('cliente/vuelos/', VerVuelosClienteView.as_view(), name='ver_vuelos_cliente'),
    path('cliente/vuelo/<int:vuelo_id>/detalles/', DetallesVueloView.as_view(), name='detalles_vuelo'),
    path('cliente/vuelo/<int:vuelo_id>/asientos/', SeleccionarAsientoView.as_view(), name='seleccionar_asiento'),

    # Rutas para Clientes (reservas)
    path('cliente/reservas/', VerReservasClienteView.as_view(), name='ver_reservas_cliente'),
    path('cliente/reservas/<str:filtro>/', VerReservasClienteView.as_view(), name='ver_reservas_cliente_filtradas'),
    path('cliente/reservas/<int:reserva_id>/cancelar/', CancelarReservaView.as_view(), name='cancelar_reserva'),

    # Rutas para Clientes (pasajeros)
    path('pasajeros/', GestionarPasajerosView.as_view(), name='gestionar_pasajeros'),
    path('pasajeros/editar/<int:pasajero_id>/', EditarPasajeroView.as_view(), name='editar_pasajero'),
    path('pasajeros/eliminar/<int:pasajero_id>/', EliminarPasajeroView.as_view(), name='eliminar_pasajero'),
    
    # Rutas para Empleados
    path('empleado/', PanelEmpleadoView.as_view(), name='panel_empleado'),
    
    # Rutas para Empleados(reservas)
    path('empleado/reservas/', GestionarReservasEmpleadoView.as_view(), name='gestionar_reservas_empleado'),
    path('empleado/reservas/<str:filtro>/', GestionarReservasEmpleadoView.as_view(), name='gestionar_reservas_empleado_filtradas'),
    path('empleado/reservas/confirmar/<int:reserva_id>/', ConfirmarReservaView.as_view(), name='confirmar_reserva'),
    path('empleado/reservas/cancelar/<int:reserva_id>/', CancelarReservaEmpleadoView.as_view(), name='cancelar_reserva'),

    # Rutas para Empleados (vuelos)
    path('empleado/vuelos/', GestionarVuelosView.as_view(), name='gestionar_vuelos_empleado'),
    path('empleado/vuelos/crear/', CrearVueloView.as_view(), name='crear_vuelo_empleado'),
    path('empleado/vuelos/editar/<int:vuelo_id>/', EditarVueloView.as_view(), name='editar_vuelo_empleado'),
    path('empleado/vuelos/eliminar/<int:vuelo_id>/', EliminarVueloView.as_view(), name='eliminar_vuelo_empleado'),
]