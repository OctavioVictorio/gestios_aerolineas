from django import forms
from home.models import Usuario
from django.core.exceptions import ValidationError

class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=150, 
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    password1 = forms.CharField(
        max_length=30, 
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )    
    password2 = forms.CharField(
        max_length=30, 
        label="Repite tu contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if Usuario.objects.filter(username=username).exists():
            raise ValidationError("El nombre de usuario ya está en uso")
        return username
    
    def clean_email(self):
        email = self.cleaned_data["email"]
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError("El correo electrónico ya está en uso")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden")
        return cleaned_data 
    

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150, 
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(
        max_length=30, 
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if not Usuario.objects.filter(username=username).exists():
            raise ValidationError("El nombre de usuario no existe")
        return username
