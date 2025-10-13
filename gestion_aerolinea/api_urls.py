from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    AvionViewSet, VueloViewSet, PasajeroViewSet, 
    ReservaViewSet, BoletoViewSet, ReportePasajerosVueloView
)

router = DefaultRouter()

# Definición de rutas CRUD (para ViewSets)
router.register(r'aviones', AvionViewSet, basename='avion')       
router.register(r'vuelos', VueloViewSet, basename='vuelo')         
router.register(r'pasajeros', PasajeroViewSet, basename='pasajero') 
router.register(r'reservas', ReservaViewSet, basename='reserva')   
router.register(r'boletos', BoletoViewSet, basename='boleto')     

urlpatterns = [
    path('', include(router.urls)),

    path(
        'reportes/vuelos/<int:vuelo_id>/pasajeros/', 
        ReportePasajerosVueloView.as_view(), 
        name='reporte-pasajeros-vuelo'
    ),
]