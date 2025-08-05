from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.urls import reverse_lazy
from .models import Vuelo, Asiento, Reserva, Pasajero
from .forms import ReservaForm

# Vista para listar vuelos disponibles (cliente)
class VerVuelosClienteView(View):
    def get(self, request):
        vuelos = Vuelo.objects.all()
        return render(request, 'cliente/ver_vuelos.html', {'vuelos': vuelos})


# Vista para seleccionar asiento (cliente)
class SeleccionarAsientoView(View):
    def get(self, request, vuelo_id):
        vuelo = get_object_or_404(Vuelo, id=vuelo_id)
        asientos_disponibles = Asiento.objects.filter(avion=vuelo.avion, estado='disponible')
        return render(request, 'cliente/seleccionar_asiento.html', {
            'vuelo': vuelo,
            'asientos': asientos_disponibles
        })


# Vista para crear una reserva (cliente)
class CrearReservaView(View):
    def post(self, request, vuelo_id, asiento_id):
        if not request.user.is_authenticated:
            return redirect('login')

        vuelo = get_object_or_404(Vuelo, id=vuelo_id)
        asiento = get_object_or_404(Asiento, id=asiento_id)
        pasajero = get_object_or_404(Pasajero, user=request.user)

        data = {
            'vuelo': vuelo.id,
            'pasajero': pasajero.id,
            'asiento': asiento.id,
            'precio_total': vuelo.precio_base,
            'codigo_reserva': get_random_string(length=10).upper(),
            'estado': 'pendiente',
        }

        form = ReservaForm(data)
        if form.is_valid():
            reserva = form.save(commit=False)
            asiento.estado = 'reservado'
            asiento.save()
            reserva.save()
            messages.success(request, f"Reserva creada con éxito. Código: {reserva.codigo_reserva}")
            return redirect('ver_reservas_cliente')
        else:
            messages.error(request, form.errors.as_text())
            return redirect('seleccionar_asiento', vuelo_id=vuelo.id)


# Vista para ver las reservas del cliente
class VerReservasClienteView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')

        pasajero = get_object_or_404(Pasajero, user=request.user)
        reservas = Reserva.objects.filter(pasajero=pasajero)
        return render(request, 'cliente/ver_reservas.html', {'reservas': reservas})
