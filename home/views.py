from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from home.models import Usuario
from django.shortcuts import redirect, render
from django.views import View
from home.forms import LoginForm, RegisterForm

class HomeView(View):
    def get(self, request):
        return render(request, "index.html")


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("index")
        form = LoginForm()
        return render(request, "accounts/login.html", {"form": form})
    
    def post(self, request):
        if request.user.is_authenticated:
            return redirect("index")
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Sesión iniciada correctamente.")
                return redirect("index")
            else:
                messages.error(request, "Usuario o contraseña incorrectos.")
        return render(request, "accounts/login.html", {"form": form})


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("index")
        form = RegisterForm()
        return render(request, "accounts/register.html", {"form": form})
    
    def post(self, request):
        if request.user.is_authenticated:
            return redirect("index")
        form = RegisterForm(request.POST)
        if form.is_valid():
            Usuario.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
                email=form.cleaned_data["email"],
                perfil='cliente'
            )
            messages.success(request, "Registrado correctamente. Ahora podés iniciar sesión.")
            return redirect("login")
        return render(request, "accounts/register.html", {"form": form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("login")
