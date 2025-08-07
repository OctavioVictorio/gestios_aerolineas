from django.urls import path
from .views import (
    PanelClienteView,
    VerVuelosClienteView,
    DetallesVueloView,
    SeleccionarAsientoView,
    VerReservasClienteView,
    CancelarReservaView,
    GestionarPasajerosView,
    EditarPasajeroView,
    EliminarPasajeroView,
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
    

]