from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.views import View
from django.db import transaction

from .forms import AvionForm, CantidadPasajerosForm, PasajeroForm, VueloForm, SeleccionarVueloForm, UsuarioForm
from .models import Asiento, Avion, Pasajero, Reserva, Vuelo


def es_cliente(user):
    return user.is_authenticated and user.perfil == 'cliente'

def es_empleado(user):
    return user.is_authenticated and user.perfil == 'empleado'

def es_admin(user):
    return user.is_authenticated and user.perfil == 'admin'

def es_empleado_o_admin(user):
    return user.is_authenticated and (user.perfil == 'empleado' or user.perfil == 'admin')

@method_decorator(login_required, name='dispatch')
class MiPerfilView(View):
    def get(self, request):
        user = request.user
        usuario_form = UsuarioForm(instance=user)
        pasajeros = Pasajero.objects.filter(usuario=user)

        context = {
            'usuario_form': usuario_form,
            'pasajeros': pasajeros,
        }
        return render(request, 'mi_perfil.html', context)
    
    def post(self, request):
        user = request.user
        usuario_form = UsuarioForm(request.POST, instance=user)

        if usuario_form.is_valid():
            usuario_form.save()
            messages.success(request, "Tu perfil de usuario ha sido actualizado.")
            return redirect('mi_perfil')

        pasajeros = Pasajero.objects.filter(usuario=user)
        context = {
            'usuario_form': usuario_form,
            'pasajeros': pasajeros,
        }
        return render(request, 'mi_perfil.html', context)
    

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


@method_decorator(login_required, name='dispatch')
class DetallesVueloView(View):
    def get(self, request, vuelo_id):
        vuelo = get_object_or_404(Vuelo, id=vuelo_id)
        cantidad_pasajeros_form = CantidadPasajerosForm() # ✅ Instancia del formulario
        return render(request, 'cliente/detalles_vuelo.html', {
            'vuelo': vuelo,
            'cantidad_pasajeros_form': cantidad_pasajeros_form, # ✅ Pasamos el formulario al contexto
        })


@method_decorator(login_required, name='dispatch')
class SeleccionarPasajerosView(View):
    def get(self, request, vuelo_id):
        vuelo = get_object_or_404(Vuelo, id=vuelo_id)
        form = CantidadPasajerosForm()
        return render(request, 'cliente/seleccionar_pasajeros.html', {'vuelo': vuelo, 'form': form})

    def post(self, request, vuelo_id):
        form = CantidadPasajerosForm(request.POST)
        if form.is_valid():
            total_pasajeros = form.cleaned_data['adultos'] + form.cleaned_data['menores']
            # ✅ Guardamos la cantidad total en la sesión
            request.session['total_pasajeros'] = total_pasajeros
            return redirect('seleccionar_asiento', vuelo_id=vuelo_id)
        else:
            vuelo = get_object_or_404(Vuelo, id=vuelo_id)
            return render(request, 'cliente/seleccionar_pasajeros.html', {'vuelo': vuelo, 'form': form})
        

@method_decorator(login_required, name='dispatch')
class SeleccionarAsientoView(View):
    def get(self, request, vuelo_id):
        vuelo = get_object_or_404(Vuelo, id=vuelo_id)
        asientos_reservados_ids = Reserva.objects.filter(
            vuelo=vuelo,
            estado__in=['confirmada', 'pendiente']
        ).values_list('asiento__id', flat=True)

        asientos_avion = {asiento.id: asiento for asiento in Asiento.objects.filter(avion=vuelo.avion)}
        layout_asientos = {}
        filas = vuelo.avion.filas
        columnas = vuelo.avion.columnas

        for fila in range(1, filas + 1):
            layout_asientos[fila] = []
            for columna in range(1, columnas + 1):
                asiento_encontrado = next(
                    (asiento for asiento in asientos_avion.values() if asiento.fila == fila and asiento.columna == columna),
                    None
                )
                layout_asientos[fila].append(asiento_encontrado)
        
        pasajeros = request.user.pasajeros_creados.all()
        pasajero_form = PasajeroForm()
        cantidad_pasajeros_form = CantidadPasajerosForm()

        total_pasajeros = request.session.get('total_pasajeros', 0)
        
        return render(request, 'cliente/seleccionar_asiento.html', {
            'vuelo': vuelo,
            'layout_asientos': layout_asientos,
            'asientos_reservados_ids': asientos_reservados_ids,
            'pasajeros': pasajeros,
            'pasajero_form': pasajero_form,
            'cantidad_pasajeros_form': cantidad_pasajeros_form,
            'total_pasajeros': total_pasajeros
        })
    def post(self, request, vuelo_id):
        vuelo = get_object_or_404(Vuelo, id=vuelo_id)
        if 'seleccionar_pasajeros_cantidad' in request.POST:
            form = CantidadPasajerosForm(request.POST)
            if form.is_valid():
                total_pasajeros = form.cleaned_data['adultos'] + form.cleaned_data['menores']
                if total_pasajeros > 0:
                    request.session['total_pasajeros'] = total_pasajeros
                else:
                    messages.error(request, 'La cantidad total de pasajeros debe ser al menos 1.')
                return redirect('seleccionar_asiento', vuelo_id=vuelo.id)
            else:
                messages.error(request, 'Por favor, introduce una cantidad válida de pasajeros.')
                return redirect('seleccionar_asiento', vuelo_id=vuelo.id)

        if 'crear_pasajero' in request.POST:
            pasajero_form = PasajeroForm(request.POST)
            if pasajero_form.is_valid():
                nuevo_pasajero = pasajero_form.save(commit=False)
                nuevo_pasajero.usuario = request.user
                nuevo_pasajero.save()
                messages.success(request, f'El pasajero {nuevo_pasajero.nombre} ha sido agregado.')
            else:
                messages.error(request, 'Error al crear el pasajero. Por favor, revisa el formulario.')
            
            return redirect('seleccionar_asiento', vuelo_id=vuelo.id)
        
        total_pasajeros = request.session.get('total_pasajeros', 0)
        asientos_seleccionados_ids = request.POST.getlist('asientos')
        pasajeros_seleccionados_ids = request.POST.getlist('pasajeros')
        
        if len(asientos_seleccionados_ids) != total_pasajeros or len(pasajeros_seleccionados_ids) != total_pasajeros:
            messages.error(request, f'Debes seleccionar {total_pasajeros} asientos y asignar un pasajero a cada uno.')
            return redirect('seleccionar_asiento', vuelo_id=vuelo.id)

        try:
            with transaction.atomic():
                for asiento_id, pasajero_id in zip(asientos_seleccionados_ids, pasajeros_seleccionados_ids):
                    asiento = get_object_or_404(Asiento, id=asiento_id)
                    pasajero = get_object_or_404(Pasajero, id=pasajero_id, usuario=request.user)

                    if Reserva.objects.filter(vuelo=vuelo, asiento=asiento, estado__in=['confirmada', 'pendiente']).exists():
                        raise ValueError(f'El asiento {asiento.numero} ya ha sido reservado.')

                    Reserva.objects.create(
                        vuelo=vuelo,
                        pasajero=pasajero,
                        asiento=asiento,
                        usuario_reserva=request.user,
                        estado='pendiente',
                        precio_total=vuelo.precio_base,
                        codigo_reserva=get_random_string(length=10).upper()
                    )
            
            del request.session['total_pasajeros']
            messages.success(request, f'Reservas creadas exitosamente para {total_pasajeros} asientos.')
            return redirect('ver_reservas_cliente')

        except ValueError as e:
            messages.error(request, str(e))
        except Exception:
            messages.error(request, 'Ocurrió un error inesperado al procesar las reservas.')

        return redirect('seleccionar_asiento', vuelo_id=vuelo.id)
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
class CrearPasajeroView(View):
    def get(self, request):
        form = PasajeroForm()
        return render(request, 'cliente/crear_pasajero.html', {'form': form})

    def post(self, request):
        form = PasajeroForm(request.POST)
        if form.is_valid():
            pasajero = form.save(commit=False)
            pasajero.usuario = request.user
            pasajero.save()
            messages.success(request, "Pasajero creado exitosamente.")
            return redirect('gestionar_pasajeros')
        
        messages.error(request, "Error al crear el pasajero. Por favor, revisa los datos.")
        return render(request, 'cliente/crear_pasajero.html', {'form': form})
    
    
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


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(es_empleado_o_admin), name='dispatch')
class GestionarAvionesView(View):
    def get(self, request):
        aviones = Avion.objects.all().order_by('modelo')
        return render(request, 'empleado/gestionar_aviones.html', {'aviones': aviones})


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(es_empleado_o_admin), name='dispatch')
class CrearAvionView(View):
    def get(self, request):
        form = AvionForm()
        return render(request, 'empleado/crear_avion.html', {'form': form})
    
    def post(self, request):
        form = AvionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Avión creado exitosamente.")
            return redirect('gestionar_aviones_empleado')
        
        return render(request, 'empleado/crear_avion.html', {'form': form})


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(es_empleado_o_admin), name='dispatch')
class EditarAvionView(View):
    def get(self, request, avion_id):
        avion = get_object_or_404(Avion, id=avion_id)
        form = AvionForm(instance=avion)
        return render(request, 'empleado/editar_avion.html', {'form': form, 'avion': avion})
    
    def post(self, request, avion_id):
        avion = get_object_or_404(Avion, id=avion_id)
        form = AvionForm(request.POST, instance=avion)
        if form.is_valid():
            form.save()
            messages.success(request, "Avión editado exitosamente.")
            return redirect('gestionar_aviones_empleado')
        
        return render(request, 'empleado/editar_avion.html', {'form': form, 'avion': avion})


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(es_empleado_o_admin), name='dispatch')
class EliminarAvionView(View):
    def post(self, request, avion_id):
        avion = get_object_or_404(Avion, id=avion_id)
        try:
            avion.delete()
            messages.success(request, f"Avión '{avion.modelo}' eliminado exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar el avión: {e}")
        
        return redirect('gestionar_aviones_empleado')


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(es_empleado_o_admin), name='dispatch')
class GestionarPasajerosEmpleadoView(View):
    def get(self, request):
        pasajeros = Pasajero.objects.all().order_by('apellido', 'nombre')
        return render(request, 'empleado/gestionar_pasajeros.html', {'pasajeros': pasajeros})


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(es_empleado_o_admin), name='dispatch')
class DetallePasajeroEmpleadoView(View):
    def get(self, request, pasajero_id):
        pasajero = get_object_or_404(Pasajero, id=pasajero_id)
        reservas = pasajero.reservas.all().order_by('-fecha_reserva')
        return render(request, 'empleado/detalle_pasajero.html', {
            'pasajero': pasajero,
            'reservas': reservas
        })
    

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(es_empleado_o_admin), name='dispatch')
class ReportePasajerosVueloView(View):
    def get(self, request):
        form = SeleccionarVueloForm()
        context = {
            'form': form,
            'reporte_data': None,
        }
        return render(request, 'empleado/reporte_pasajeros_vuelo.html', context)
    
    def post(self, request):
        form = SeleccionarVueloForm(request.POST)
        context = {'form': form, 'reporte_data': None}

        if form.is_valid():
            vuelo_seleccionado = form.cleaned_data['vuelo']
            reservas = Reserva.objects.filter(
                vuelo=vuelo_seleccionado,
                estado='confirmada'
            ).order_by('asiento__numero')
            
            context['reporte_data'] = {
                'vuelo': vuelo_seleccionado,
                'pasajeros': [reserva.pasajero for reserva in reservas],
                'reservas': reservas,
            }
        
        return render(request, 'empleado/reporte_pasajeros_vuelo.html', context)