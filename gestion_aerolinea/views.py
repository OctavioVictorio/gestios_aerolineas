from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.views import View

from .forms import PasajeroForm, ReservaForm
from .models import Asiento, Pasajero, Reserva, Vuelo 



@method_decorator(login_required, name='dispatch')
class PanelClienteView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.perfil != 'cliente':
            return redirect('index')
        return render(request, 'cliente/panel_cliente.html')


class VerVuelosClienteView(View):
    def get(self, request):
        vuelos = Vuelo.objects.all()
        return render(request, 'cliente/ver_vuelos.html', {'vuelos': vuelos})


class DetallesVueloView(View):
    def get(self, request, vuelo_id):
        vuelo = get_object_or_404(Vuelo, id=vuelo_id)
        context = {
            'vuelo': vuelo,
        }
        return render(request, 'cliente/detalles_vuelo.html', context)


@method_decorator(login_required, name='dispatch')
class SeleccionarAsientoView(View):
    def get(self, request, vuelo_id):
        vuelo = get_object_or_404(Vuelo, id=vuelo_id)
        
        asientos = Asiento.objects.filter(avion=vuelo.avion).order_by('fila', 'columna')
        layout_asientos = {}
        for asiento in asientos:
            if asiento.fila not in layout_asientos:
                layout_asientos[asiento.fila] = []
            layout_asientos[asiento.fila].append(asiento)
        
        pasajeros = request.user.pasajeros_creados.all()
        form = ReservaForm()
        form.fields['pasajero'].queryset = pasajeros
        
        return render(request, 'cliente/seleccionar_asiento.html', {
            'vuelo': vuelo,
            'layout_asientos': layout_asientos,
            'pasajeros': pasajeros,
            'form': form,
        })
    def post(self, request, vuelo_id):
        vuelo = get_object_or_404(Vuelo, id=vuelo_id)
        pasajeros = request.user.pasajeros_creados.all()
        
        form = ReservaForm(request.POST)
        form.fields['pasajero'].queryset = pasajeros
        
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario_reserva = request.user
            reserva.vuelo = vuelo
            
            reserva.codigo_reserva = get_random_string(length=10).upper()
            reserva.estado = 'pendiente'
            reserva.precio_total = vuelo.precio_base
            
            reserva.save()
            
            asiento = reserva.asiento
            asiento.estado = 'reservado'
            asiento.save()
            
            messages.success(request, f'¡Reserva para el asiento {asiento.numero} realizada con éxito! Código: {reserva.codigo_reserva}')
            return redirect('ver_reservas_cliente')
        
        messages.error(request, 'Por favor, revisa los datos del formulario.')
        
        asientos = Asiento.objects.filter(avion=vuelo.avion).order_by('fila', 'columna')
        layout_asientos = {}
        for asiento in asientos:
            if asiento.fila not in layout_asientos:
                layout_asientos[asiento.fila] = []
            layout_asientos[asiento.fila].append(asiento)
        
        return render(request, 'cliente/seleccionar_asiento.html', {
            'vuelo': vuelo,
            'layout_asientos': layout_asientos,
            'pasajeros': pasajeros,
            'form': form,
        })


@method_decorator(login_required, name='dispatch')
class VerReservasClienteView(View):
    def get(self, request, filtro=None):
        if not request.user.is_authenticated:
            return redirect('login')

        if filtro:
            reservas = Reserva.objects.filter(
                usuario_reserva=request.user, estado=filtro
            ).order_by('-fecha_reserva')
        else:
            reservas = Reserva.objects.filter(usuario_reserva=request.user).order_by('-fecha_reserva')
        
        return render(request, 'cliente/ver_reservas.html', {
            'reservas': reservas,
            'filtro_activo': filtro 
        })


@method_decorator(login_required, name='dispatch')
class CancelarReservaView(View):
    def post(self, request, reserva_id):
        reserva = get_object_or_404(Reserva, id=reserva_id, usuario_reserva=request.user)
        asiento = reserva.asiento
        asiento.estado = 'disponible'
        asiento.save()
        reserva.estado = 'cancelada'
        reserva.save()

        messages.success(request, f'La reserva con código {reserva.codigo_reserva} ha sido cancelada exitosamente.')
        return redirect('ver_reservas_cliente')


@method_decorator(login_required, name='dispatch')
class GestionarPasajerosView(View):
    def get(self, request):
        pasajeros = Pasajero.objects.filter(usuario=request.user)
        form = PasajeroForm()
        return render(request, 'cliente/gestionar_pasajeros.html', {
            'pasajeros': pasajeros,
            'form': form
        })

    def post(self, request):
        form = PasajeroForm(request.POST)
        if form.is_valid():
            pasajero = form.save(commit=False)
            pasajero.usuario = request.user
            pasajero.save()
            messages.success(request, "Pasajero registrado con éxito.")
            return redirect('gestionar_pasajeros')
        
        pasajeros = Pasajero.objects.filter(usuario=request.user)
        messages.error(request, "Error al registrar el pasajero. Por favor, revisa los datos.")
        return render(request, 'cliente/gestionar_pasajeros.html', {
            'pasajeros': pasajeros,
            'form': form
        })


@method_decorator(login_required, name='dispatch')
class EditarPasajeroView(View):
    def get(self, request, pasajero_id):
        pasajero = get_object_or_404(Pasajero, id=pasajero_id, usuario=request.user)
        form = PasajeroForm(instance=pasajero)
        return render(request, 'cliente/editar_pasajero.html', {
            'form': form,
            'pasajero': pasajero
        })
        
    def post(self, request, pasajero_id):
        pasajero = get_object_or_404(Pasajero, id=pasajero_id, usuario=request.user)
        form = PasajeroForm(request.POST, instance=pasajero)
        if form.is_valid():
            form.save()
            messages.success(request, "Pasajero actualizado con éxito.")
            return redirect('gestionar_pasajeros')
        
        messages.error(request, "Error al actualizar el pasajero. Por favor, revisa los datos.")
        return render(request, 'cliente/editar_pasajero.html', {
            'form': form,
            'pasajero': pasajero
        })


@method_decorator(login_required, name='dispatch')
class EliminarPasajeroView(View):
    def post(self, request, pasajero_id):
        pasajero = get_object_or_404(Pasajero, id=pasajero_id, usuario=request.user)
        pasajero.delete()
        messages.success(request, "Pasajero eliminado con éxito.")
        return redirect('gestionar_pasajeros')


