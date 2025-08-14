from django.db import models
from home.models import Usuario 


class Avion(models.Model):
    modelo = models.CharField(max_length=100)
    capacidad = models.IntegerField(editable=False)
    filas = models.IntegerField()
    columnas = models.IntegerField()

    def save(self, *args, **kwargs):
        self.capacidad = self.filas * self.columnas
        
        super().save(*args, **kwargs)

        if not self.asientos.exists():
            for fila_num in range(1, self.filas + 1):
                for columna_num in range(1, self.columnas + 1):
                    numero_asiento = f"{fila_num}-{columna_num}" 
                    Asiento.objects.create(
                        avion=self,
                        numero=numero_asiento,
                        fila=fila_num,
                        columna=columna_num,
                        estado='disponible',
                        tipo='economica' 
                    )
    def __str__(self):
        return f"{self.modelo} ({self.capacidad} asientos)"

class Vuelo(models.Model):
    imagen = models.ImageField(upload_to='vuelos_imagenes/', null=True, blank=True)
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    fecha_salida = models.DateTimeField()
    fecha_llegada = models.DateTimeField()
    duracion = models.DurationField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=[
        ('programado', 'Programado'),
        ('cancelado', 'Cancelado'),
        ('en curso', 'En curso'),
        ('finalizado', 'Finalizado'),
    ])
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    avion = models.ForeignKey(Avion, on_delete=models.CASCADE)

    def __str__(self):
        return f"Vuelo de {self.origen} a {self.destino} ({self.fecha_salida.date()})"
    
    def save(self, *args, **kwargs):
        if self.fecha_llegada < self.fecha_salida:
            raise ValueError("La fecha de llegada no puede ser anterior a la fecha de salida.")
        elif self.duracion is None:
            self.duracion = self.fecha_llegada - self.fecha_salida
        super().save(*args, **kwargs)


class Pasajero(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pasajeros_creados')
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    tipo_documento = models.CharField(max_length=20, choices=[
        ('dni', 'DNI'),
        ('pasaporte', 'Pasaporte'),
        ('otro', 'Otro'),
    ])
    numero_documento = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField()
    def edad(self):
        from datetime import date
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.get_tipo_documento_display()}: {self.numero_documento}"


class Asiento(models.Model):
    TIPO_ASIENTO = [
        ('economica', 'Económica'),
        ('ejecutiva', 'Ejecutiva'),
        ('premium', 'Premium'),
    ]

    ESTADO_ASIENTO = [
        ('disponible', 'Disponible'),
        ('reservado', 'Reservado'),
        ('ocupado', 'Ocupado'),
    ]

    avion = models.ForeignKey(Avion, on_delete=models.CASCADE, related_name='asientos')
    numero = models.CharField(max_length=10) 
    fila = models.IntegerField()
    columna = models.IntegerField() 
    tipo = models.CharField(max_length=20, choices=TIPO_ASIENTO, default='economica')
    estado = models.CharField(max_length=20, choices=ESTADO_ASIENTO, default='disponible')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['avion', 'fila', 'columna'], name='unico_asiento')
        ]
        ordering = ['fila', 'columna']

    def __str__(self):
        return f"Asiento {self.numero} ({self.get_tipo_display()}) - {self.avion.modelo}"


class Reserva(models.Model):
    vuelo = models.ForeignKey(Vuelo, on_delete=models.CASCADE, related_name='reservas')
    pasajero = models.ForeignKey(Pasajero, on_delete=models.CASCADE, related_name='reservas')
    asiento = models.ForeignKey(Asiento, on_delete=models.CASCADE, related_name='reservas')
    usuario_reserva = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='reservas_creadas'
    )
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ], default='pendiente')
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)
    codigo_reserva = models.CharField(max_length=20, unique=True)

    class Meta:
        unique_together = ('vuelo', 'asiento')

    def __str__(self):
        return f"Reserva de {self.pasajero} en {self.vuelo} - Asiento: {self.asiento.numero}"


class Boleto(models.Model):
    ESTADO_BOLETO = [
        ('emitido', 'Emitido'),
        ('cancelado', 'Cancelado'),
        ('usado', 'Usado'),
    ]

    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, related_name='boleto')
    codigo_barra = models.CharField(max_length=100, unique=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_BOLETO, default='emitido')

    def __str__(self):
        return f"Boleto de {self.reserva.pasajero} - Código: {self.codigo_barra}"
