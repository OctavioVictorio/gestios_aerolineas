from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Avion, Vuelo, Pasajero, Reserva, Asiento, Boleto
from .serializers import (
    AvionSerializer, VueloReadSerializer, VueloCreateUpdateSerializer, 
    PasajeroSerializer, AsientoSerializer, 
    ReservaReadSerializer, ReservaCreateSerializer, ReservaEstadoUpdateSerializer,
    BoletoSerializer, ReportePasajeroVueloSerializer
)
from .permissions import IsAdmin, IsAdminOrReadOnly, IsClienteOrAdmin
from .services import ReservaService, ReporteService


# 1. CRUD: AVIONES (ADMINISTRADOR)
class AvionViewSet(viewsets.ModelViewSet):
    """Permite el CRUD de Aviones. Restringido a Admin."""
    queryset = Avion.objects.all()
    serializer_class = AvionSerializer
    permission_classes = [IsAdmin] 


# 2. CRUD: VUELOS (ADMINISTRADOR / LECTURA PARA TODOS)
class VueloViewSet(viewsets.ModelViewSet):
    """Permite Listar/Detalle (Todos) y CRUD (Admin)."""
    queryset = Vuelo.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        """Usa serializadores diferentes para lectura vs escritura."""
        if self.action in ['list', 'retrieve', 'asientos_disponibles']:
            return VueloReadSerializer
        return VueloCreateUpdateSerializer

    @action(detail=True, methods=['get'], url_path='asientos-disponibles', permission_classes=[IsAdminOrReadOnly])
    def asientos_disponibles(self, request, pk=None):
        """Muestra el layout de asientos de un vuelo y marca los reservados."""
        vuelo = self.get_object()
        
        asientos_ocupados_ids = Reserva.objects.filter(
            vuelo=vuelo, 
            estado__in=['pendiente', 'confirmada']
        ).values_list('asiento_id', flat=True)
        
        asientos = Asiento.objects.filter(avion=vuelo.avion).order_by('fila', 'columna')

        serializer = AsientoSerializer(asientos, many=True)
        data = serializer.data
        
        for item in data:
            if item['id'] in asientos_ocupados_ids:
                item['estado'] = 'reservado' 
            else:
                item['estado'] = 'disponible' 
            
        return Response(data)


# 3. CRUD: PASAJEROS (ADMIN / CLIENTE (Self-CRUD))
class PasajeroViewSet(viewsets.ModelViewSet):
    """Permite CRUD (Admin) y Create/Read/Update (Cliente sobre sí mismo)."""
    serializer_class = PasajeroSerializer
    permission_classes = [IsClienteOrAdmin] 
    
    def perform_create(self, serializer):
        """Asigna el usuario que crea el registro (cliente auto-registrándose)."""
        serializer.save(usuario=self.request.user)
    
    def get_queryset(self):
        """Restringe la vista a los propios pasajeros si no es Admin/Empleado."""
        user = self.request.user
        if user.is_authenticated and user.perfil == 'cliente':
            return Pasajero.objects.filter(usuario=user)
        return Pasajero.objects.all()


# 4. RESERVAS (CREACIÓN Y ACCIONES)
class ReservaViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    """
    Gestiona la creación, listado y detalle de Reservas.
    Las acciones 'confirmar' y 'cancelar' están enlazadas aquí.
    """
    queryset = Reserva.objects.all()
    permission_classes = [IsClienteOrAdmin]
    
    def get_serializer_class(self):
        """Usa el serializer de creación para POST y el de lectura para GET."""
        if self.action == 'create':
            return ReservaCreateSerializer
        return ReservaReadSerializer
    
    def get_queryset(self):
        """Restringe la vista a las propias reservas si no es Admin/Empleado."""
        user = self.request.user
        if user.is_authenticated and user.perfil == 'cliente':
            return Reserva.objects.filter(usuario_reserva=user)
        return Reserva.objects.all()

    def create(self, request, *args, **kwargs):
        """Crea una reserva utilizando el ReservaService."""
        serializer = ReservaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        try:
            reserva = ReservaService.crear_reserva(
                vuelo_id=data['vuelo'].id,
                numero_documento=data['pasajero'].numero_documento, 
                asiento_id=data['asiento'].id,
                usuario_reserva=request.user
            )
            return Response(ReservaReadSerializer(reserva).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], serializer_class=ReservaEstadoUpdateSerializer, 
            permission_classes=[IsAdmin], url_path='confirmar')
    def confirmar(self, request, pk=None):
        """Confirma una reserva (genera boleto). Solo Admin/Empleado."""
        try:
            reserva = self.get_object()
            reserva_actualizada, mensaje = ReservaService.cambiar_estado_reserva(
                reserva_id=reserva.id, 
                nuevo_estado='confirmada'
            )
            return Response({
                'detail': mensaje,
                'reserva': ReservaReadSerializer(reserva_actualizada).data
            })
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], serializer_class=ReservaEstadoUpdateSerializer, 
            permission_classes=[IsClienteOrAdmin], url_path='cancelar')
    def cancelar(self, request, pk=None):
        """Cancela una reserva. Admin o Cliente (debe ser el dueño)."""
        try:
            reserva = self.get_object()
            
            self.check_object_permissions(request, reserva) 
            
            reserva_actualizada, mensaje = ReservaService.cambiar_estado_reserva(
                reserva_id=reserva.id, 
                nuevo_estado='cancelada'
            )
            return Response({
                'detail': mensaje,
                'reserva': ReservaReadSerializer(reserva_actualizada).data
            })
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 5. BOLETOS (LECTURA)
class BoletoViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    """Permite Listar y Consultar Detalle de Boletos (Admin/Cliente-Dueño)."""
    queryset = Boleto.objects.all()
    serializer_class = BoletoSerializer
    permission_classes = [IsClienteOrAdmin]

    def get_queryset(self):
        """Restringe la vista a los propios boletos si no es Admin/Empleado."""
        user = self.request.user
        if user.is_authenticated and user.perfil == 'cliente':
            return Boleto.objects.filter(reserva__usuario_reserva=user)
        return Boleto.objects.all()


# 6. REPORTES (Admin/Empleado)
class ReportePasajerosVueloView(APIView):
    """Endpoint para el listado de pasajeros confirmados por vuelo."""
    permission_classes = [IsAdmin] 
    
    def get(self, request, vuelo_id, format=None):
        """GET /api/v1/reportes/vuelos/<vuelo_id>/pasajeros/"""
        try:
            reporte_data, vuelo_obj = ReporteService.listar_pasajeros_por_vuelo(vuelo_id)
            
            serializer = ReportePasajeroVueloSerializer(reporte_data, many=True)
            
            response_data = {
                'vuelo': VueloReadSerializer(vuelo_obj).data,
                'total_pasajeros_confirmados': len(reporte_data),
                'pasajeros': serializer.data
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_404_NOT_FOUND)