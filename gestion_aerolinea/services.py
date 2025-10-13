from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.db.models import F

from .models import Asiento, Boleto, Pasajero, Reserva, Vuelo

class ReservaService:
    """Clase de servicio para manejar toda la lógica de negocio relacionada con Reservas."""
    
    @staticmethod
    def crear_reserva(vuelo_id, numero_documento, asiento_id, usuario_reserva):
        """
        Crea una o más reservas. 
        Esta lógica replica y mejora la que tenías en SeleccionarAsientoView.post().
        """
        try:
            with transaction.atomic():
                vuelo = get_object_or_404(Vuelo, id=vuelo_id)
                asiento = get_object_or_404(Asiento, id=asiento_id)
                pasajero = Pasajero.objects.get(numero_documento=numero_documento) 
                
                if Reserva.objects.filter(vuelo=vuelo, asiento=asiento, estado__in=['confirmada', 'pendiente']).exists():
                    raise ValueError(f'El asiento {asiento.numero} ya ha sido reservado para este vuelo.')
                
                if Reserva.objects.filter(vuelo=vuelo, pasajero=pasajero, estado__in=['confirmada', 'pendiente']).exists():
                    raise ValueError("El pasajero ya tiene una reserva activa para este vuelo.")
                
                reserva = Reserva.objects.create(
                    vuelo=vuelo,
                    pasajero=pasajero,
                    asiento=asiento,
                    usuario_reserva=usuario_reserva, 
                    estado='pendiente',
                    precio_total=vuelo.precio_base, 
                    codigo_reserva=get_random_string(length=10).upper()
                )

                return reserva

        except Pasajero.DoesNotExist:
            raise ValueError(f"Pasajero con documento {numero_documento} no existe.")
        except Exception as e:
            raise Exception(f"Error al procesar la reserva: {str(e)}")


    @staticmethod
    def cambiar_estado_reserva(reserva_id, nuevo_estado, request_user=None):
        """
        Cambia el estado de una reserva (confirmada o cancelada).
        Lógica extraída de ConfirmarReservaView y CancelarReservaView.
        """
        reserva = get_object_or_404(Reserva, id=reserva_id)

        if nuevo_estado == 'cancelada':
            reserva.estado = 'cancelada'
            reserva.save()
            return reserva, "Reserva cancelada."
        
        elif nuevo_estado == 'confirmada':
            if reserva.estado != 'pendiente':
                raise ValueError(f"La reserva {reserva.codigo_reserva} ya no está en estado pendiente.")
            
            with transaction.atomic():
                reserva.estado = 'confirmada'
                reserva.save()

                codigo_boleto = get_random_string(length=12).upper()
                boleto = Boleto.objects.create(
                    reserva=reserva,
                    codigo_barra=codigo_boleto
                )
                return reserva, f"Reserva confirmada. Boleto generado: {boleto.codigo_barra}"
        
        else:
            raise ValueError(f"Estado '{nuevo_estado}' no válido para cambio.")


class BoletoService:
    """Clase de servicio para manejar la lógica de Boletos."""

    @staticmethod
    def generar_boleto_desde_reserva(reserva_id):
        """
        Genera un boleto para una reserva confirmada. 
        Esto se usa como API para el requisito 'Generar boleto'.
        """
        reserva = get_object_or_404(Reserva, id=reserva_id)

        if reserva.estado != 'confirmada':
            raise ValueError("El boleto solo puede generarse para reservas confirmadas.")

        if hasattr(reserva, 'boleto'):
            return reserva.boleto
        
        codigo_boleto = get_random_string(length=12).upper()
        boleto = Boleto.objects.create(
            reserva=reserva,
            codigo_barra=codigo_boleto,
            estado='emitido'
        )
        return boleto


class ReporteService:
    """Clase de servicio para generar reportes."""

    @staticmethod
    def listar_pasajeros_por_vuelo(vuelo_id):
        """
        Genera el listado de pasajeros confirmados para un vuelo.
        Mejora la lógica de ReportePasajerosVueloView usando Querysets.
        """
        vuelo = get_object_or_404(Vuelo, id=vuelo_id)
        
        reporte_data = Reserva.objects.filter(
            vuelo=vuelo,
            estado='confirmada'
        ).select_related('pasajero', 'asiento').annotate(
            nombre=F('pasajero__nombre'),
            apellido=F('pasajero__apellido'),
            numero_documento=F('pasajero__numero_documento'),
            email=F('pasajero__email'),
            asiento_numero=F('asiento__numero'),
            reserva_estado=F('estado'),
            codigo_reserva=F('codigo_reserva')
        ).values(
            'nombre', 'apellido', 'numero_documento', 'email', 
            'asiento_numero', 'reserva_estado', 'codigo_reserva'
        ).order_by('asiento__fila', 'asiento__columna') 

        return reporte_data, vuelo