from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def home(request):
    return render(request, 'public/home.html')

# Vista de Login (Acceso Dueño)
def admin_login(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')  # Si ya está logeado, redirige al panel

    if request.method == 'POST':
        usuario = request.POST.get('username')
        clave = request.POST.get('password')
        
        user = authenticate(request, username=usuario, password=clave)
        
        if user is not None:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'admin-panel/login.html')

# Vista Principal del Panel Administrativo (PROTEGIDA)
@login_required(login_url='admin_login')
def admin_dashboard(request):
    return render(request, 'admin-panel/dashboard.html')

# Vista para cerrar sesión
def admin_logout(request):
    logout(request)
    return redirect('admin_login')

# Vistas temporales de prueba para evitar errores con los {% url %} del HTML
def recorridos_list(request):
    return render(request, 'public/home.html') # Temporal

def paradas_list(request):
    return render(request, 'public/home.html') # Temporal

def atractivos_list(request):
    return render(request, 'public/home.html') # Temporal