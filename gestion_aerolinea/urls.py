from django.urls import path
from .views import (
    PanelClienteView,
    VerVuelosClienteView,
    DetallesVueloView,
    SeleccionarAsientoView,
)

urlpatterns = [
    # Rutas para clientes 
    path('cliente/', PanelClienteView.as_view(), name='panel_cliente'),
    
    # Rutas para Clientes (vuelos)
    path('cliente/vuelos/', VerVuelosClienteView.as_view(), name='ver_vuelos_cliente'),
    path('cliente/vuelo/<int:vuelo_id>/detalles/', DetallesVueloView.as_view(), name='detalles_vuelo'),
    path('cliente/vuelo/<int:vuelo_id>/asientos/', SeleccionarAsientoView.as_view(), name='seleccionar_asiento'),


]