from django import forms
from .models import Avion, Pasajero, Reserva, Vuelo, Usuario


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['pasajero', 'asiento'] 



    
class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
        }


class CantidadPasajerosForm(forms.Form):
    adultos = forms.IntegerField(label="Adultos (Desde 18 años)", min_value=1, initial=1)
    menores = forms.IntegerField(label="Menores (Hasta 17 años)", min_value=0, initial=0)


class PasajeroForm(forms.ModelForm):
    class Meta:
        model = Pasajero
        fields = ['nombre', 'apellido', 'tipo_documento', 'numero_documento', 'fecha_nacimiento', 'email', 'telefono']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-control'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }


class VueloForm(forms.ModelForm):
    class Meta:
        model = Vuelo
        fields = [
            'origen',
            'destino',
            'fecha_salida',
            'fecha_llegada',
            'estado',
            'precio_base',
            'avion',
        ]
        widgets = {
            'origen': forms.TextInput(attrs={'class': 'form-control'}),
            'destino': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_salida': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'fecha_llegada': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'precio_base': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 150.00'}),
            'avion': forms.Select(attrs={'class': 'form-control'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        fecha_salida = cleaned_data.get("fecha_salida")
        fecha_llegada = cleaned_data.get("fecha_llegada")

        if fecha_salida and fecha_llegada:
            if fecha_llegada <= fecha_salida:
                raise forms.ValidationError(
                    "La fecha y hora de llegada no pueden ser iguales o anteriores a la de salida."
                )
        
        return cleaned_data


class AvionForm(forms.ModelForm):
    class Meta:
        model = Avion
        fields = ['modelo', 'filas', 'columnas'] 
        widgets = {
            'modelo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Boeing 747'}),
            'filas': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 50'}),
            'columnas': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 6'}),
        }


class SeleccionarVueloForm(forms.Form):
    vuelo = forms.ModelChoiceField(
        queryset=Vuelo.objects.all().order_by('fecha_salida', 'origen', 'destino'),
        label="Selecciona un vuelo",
        widget=forms.Select(attrs={'class': 'form-control'})
    )