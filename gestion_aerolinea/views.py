from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.views import View

from .forms import PasajeroForm, ReservaForm, VueloForm
from .models import Asiento, Pasajero, Reserva, Vuelo 


def es_cliente(user):
    return user.is_authenticated and user.perfil == 'cliente'

def es_empleado(user):
    return user.is_authenticated and user.perfil == 'empleado'

def es_admin(user):
    return user.is_authenticated and user.perfil == 'admin'

def es_empleado_o_admin(user):
    return user.is_authenticated and (user.perfil == 'empleado' or user.perfil == 'admin')

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(es_cliente), name='dispatch')
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


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(es_empleado), name='dispatch')
class PanelEmpleadoView(View):
    def get(self, request):
        return render(request, 'empleado/panel_empleado.html')
    

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(es_empleado_o_admin), name='dispatch')
class GestionarReservasEmpleadoView(View):
    def get(self, request, filtro=None):
        if filtro:
            reservas = Reserva.objects.filter(estado=filtro).order_by('-fecha_reserva')
        else:
            reservas = Reserva.objects.all().order_by('-fecha_reserva')
        
        return render(request, 'empleado/gestionar_reservas.html', {
            'reservas': reservas,
            'filtro_activo': filtro,
        })
    

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(es_empleado_o_admin), name='dispatch')
class ConfirmarReservaView(View):
    def post(self, request, reserva_id):
        reserva = get_object_or_404(Reserva, id=reserva_id)
        if reserva.estado == 'pendiente':
            reserva.estado = 'confirmada'
            reserva.save()
            messages.success(request, f"La reserva {reserva.codigo_reserva} ha sido confirmada con éxito.")
        else:
            messages.warning(request, f"La reserva {reserva.codigo_reserva} ya no está en estado pendiente.")
        
        # Redirigimos al usuario a la página de reservas del empleado, manteniendo el filtro activo
        return redirect('gestionar_reservas_empleado')
    

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(es_empleado_o_admin), name='dispatch')
class CancelarReservaEmpleadoView(View):
    def post(self, request, reserva_id):
        reserva = get_object_or_404(Reserva, id=reserva_id)
        if reserva.estado != 'cancelada':
            reserva.estado = 'cancelada'
            reserva.save()
            messages.success(request, f"La reserva {reserva.codigo_reserva} ha sido cancelada con éxito.")
        else:
            messages.warning(request, f"La reserva {reserva.codigo_reserva} ya estaba cancelada.")
        
        return redirect(request.META.get('HTTP_REFERER', 'gestionar_reservas_empleado'))


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(es_empleado_o_admin), name='dispatch')
class GestionarVuelosView(View):
    def get(self, request):
        vuelos = Vuelo.objects.all().order_by('-fecha_salida')
        return render(request, 'empleado/gestionar_vuelos.html', {'vuelos': vuelos})


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(es_empleado_o_admin), name='dispatch')
class EditarVueloView(View):
    def get(self, request, vuelo_id):
        vuelo = get_object_or_404(Vuelo, id=vuelo_id)
        form = VueloForm(instance=vuelo)
        return render(request, 'empleado/editar_vuelo.html', {'form': form, 'vuelo': vuelo})

    def post(self, request, vuelo_id):
        vuelo = get_object_or_404(Vuelo, id=vuelo_id)
        form = VueloForm(request.POST, instance=vuelo)
        if form.is_valid():
            form.save()
            messages.success(request, "Vuelo actualizado exitosamente.")
            return redirect('gestionar_vuelos_empleado')
        return render(request, 'empleado/editar_vuelo.html', {'form': form, 'vuelo': vuelo})
        

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(es_empleado_o_admin), name='dispatch')
class EliminarVueloView(View):
    def post(self, request, vuelo_id):
        vuelo = get_object_or_404(Vuelo, id=vuelo_id)
        vuelo.delete()
        messages.success(request, "Vuelo eliminado exitosamente.")
        return redirect('gestionar_vuelos_empleado')
    

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(es_empleado_o_admin), name='dispatch')
class CrearVueloView(View):
    def get(self, request):
        form = VueloForm()
        return render(request, 'empleado/crear_vuelo.html', {'form': form})
    
    def post(self, request):
        form = VueloForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Vuelo creado exitosamente.")
            return redirect('gestionar_vuelos_empleado')
        
        return render(request, 'empleado/crear_vuelo.html', {'form': form})