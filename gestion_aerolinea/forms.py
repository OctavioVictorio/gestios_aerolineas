from django import forms
from .models import Pasajero, Reserva, Vuelo


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['pasajero', 'asiento'] 
    def clean(self):
        cleaned_data = super().clean()
        asiento = cleaned_data.get('asiento')
        
        if not asiento:
            raise forms.ValidationError('Debes seleccionar un asiento.')

        if asiento.estado != 'disponible':
            raise forms.ValidationError('El asiento seleccionado no está disponible.')
        return cleaned_data


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