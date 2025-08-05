from django import forms
from .models import Reserva

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        asiento = cleaned_data.get('asiento')

        if asiento and asiento.estado != 'disponible':
            raise forms.ValidationError("Ese asiento no está disponible.")

        return cleaned_data
