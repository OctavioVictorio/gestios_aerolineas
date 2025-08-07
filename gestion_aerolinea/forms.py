from django import forms
from .models import Pasajero, Reserva


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


