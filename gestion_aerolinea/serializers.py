from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Avion, Vuelo, Pasajero, Reserva, Asiento, Boleto


class AvionSerializer(serializers.ModelSerializer):
    """Serializer para la Gestión de Aviones y obtención de Layout."""
    class Meta:
        model = Avion
        fields = ['id', 'modelo', 'capacidad', 'filas', 'columnas'] 
        read_only_fields = ['capacidad'] 


class AsientoSerializer(serializers.ModelSerializer):
    """Serializer para obtener el detalle/layout de un asiento."""
    class Meta:
        model = Asiento
        fields = ['id', 'numero', 'fila', 'columna', 'tipo', 'estado']


class PasajeroSerializer(serializers.ModelSerializer):
    """Serializer para el Registro, Edición y Consulta de Pasajeros."""
    numero_documento = serializers.CharField(
        validators=[UniqueValidator(queryset=Pasajero.objects.all(), message="Ya existe un pasajero con este número de documento.")]
    )
    
    class Meta:
        model = Pasajero
        fields = [
            'id', 'nombre', 'apellido', 'tipo_documento', 'numero_documento',
            'email', 'telefono', 'fecha_nacimiento', 'usuario' 
        ]
        read_only_fields = ['usuario'] 


class VueloReadSerializer(serializers.ModelSerializer):
    """
    Serializer de LECTURA para Vuelos. Muestra información detallada del avión anidada.
    """
    avion = AvionSerializer(read_only=True) 
    
    class Meta:
        model = Vuelo
        fields = [
            'id', 'origen', 'destino', 'fecha_salida', 'fecha_llegada', 
            'duracion', 'estado', 'precio_base', 'avion', 'imagen'
        ]
        read_only_fields = ['duracion']


class VueloCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer de ESCRITURA para Vuelos (POST/PUT/PATCH).
    """
    class Meta:
        model = Vuelo
        fields = [
            'origen', 'destino', 'fecha_salida', 'fecha_llegada', 
            'estado', 'precio_base', 'avion', 'imagen'
        ]
        read_only_fields = ['duracion']

    def validate(self, data):
        fecha_salida = data.get('fecha_salida')
        fecha_llegada = data.get('fecha_llegada')

        if fecha_salida and fecha_llegada and fecha_llegada < fecha_salida:
            raise serializers.ValidationError("La fecha de llegada no puede ser anterior a la fecha de salida.")
        
        return data


class ReservaCreateSerializer(serializers.Serializer):
    """
    Serializer de CREACIÓN para Reservas. 
    Usa IDs de Vuelo/Asiento y el documento para encontrar al pasajero.
    """
    vuelo_id = serializers.PrimaryKeyRelatedField(queryset=Vuelo.objects.all(), source='vuelo')
    asiento_id = serializers.PrimaryKeyRelatedField(queryset=Asiento.objects.all(), source='asiento')
    numero_documento = serializers.CharField(max_length=20) 

    def validate(self, data):
        """Validación crítica: asiento y pasajero únicos por vuelo."""
        vuelo = data.get('vuelo')
        asiento = data.get('asiento')
        numero_documento = data.get('numero_documento')
        
        if asiento.avion != vuelo.avion:
            raise serializers.ValidationError("El asiento seleccionado no pertenece al avión asignado a este vuelo.")

        if Reserva.objects.filter(vuelo=vuelo, asiento=asiento, estado__in=['pendiente', 'confirmada']).exists():
            raise serializers.ValidationError("El asiento ya se encuentra reservado para este vuelo (o está pendiente).")
        
        try:
            pasajero = Pasajero.objects.get(numero_documento=numero_documento)
            if Reserva.objects.filter(vuelo=vuelo, pasajero=pasajero, estado__in=['pendiente', 'confirmada']).exists():
                raise serializers.ValidationError(f"El pasajero {pasajero.nombre} {pasajero.apellido} ya tiene una reserva activa para este vuelo.")
            
            data['pasajero'] = pasajero 
        except Pasajero.DoesNotExist:
            raise serializers.ValidationError({"numero_documento": "Pasajero no encontrado. Debe registrarse primero."})

        return data


class ReservaEstadoUpdateSerializer(serializers.Serializer):
    """Serializer vacío usado para las acciones de confirmar/cancelar (PATCH)."""
    pass


class ReservaReadSerializer(serializers.ModelSerializer):
    """Serializer para devolver el detalle y listar las reservas."""
    vuelo = VueloReadSerializer(read_only=True) 
    asiento = AsientoSerializer(read_only=True)
    pasajero = PasajeroSerializer(read_only=True)
    
    class Meta:
        model = Reserva
        fields = [
            'id', 'codigo_reserva', 'estado', 'fecha_reserva', 
            'precio_total', 'vuelo', 'asiento', 'pasajero', 'usuario_reserva'
        ]
        depth = 1 


class BoletoSerializer(serializers.ModelSerializer):
    """Serializer para la consulta de información de un Boleto."""
    reserva_info = ReservaReadSerializer(source='reserva', read_only=True) 

    class Meta:
        model = Boleto
        fields = ['id', 'codigo_barra', 'fecha_emision', 'estado', 'reserva_info']


class ReportePasajeroVueloSerializer(serializers.Serializer):
    """
    Serializer para el reporte de pasajeros por vuelo. 
    Mapea la salida del ReporteService.
    """
    nombre = serializers.CharField()
    apellido = serializers.CharField()
    numero_documento = serializers.CharField()
    email = serializers.EmailField()
    asiento_numero = serializers.CharField() 
    reserva_estado = serializers.CharField()
    codigo_reserva = serializers.CharField()