from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Recorrido, Parada
from django.views.generic import ListView, DetailView

class ParadaListView(ListView):
    model = Parada
    template_name = 'public/paradas_list.html'
    context_object_name = 'paradas'
    paginate_by = 6  # Paginación nativa de Django

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(nombre__icontains=query) | queryset.filter(direccion__icontains=query)
        return queryset

# Detalle de una Parada específica (Muestra foto, descripción y atractivos cercanos)
class ParadaDetailView(DetailView):
    model = Parada
    template_name = 'public/parada_detail.html'
    context_object_name = 'parada'

class RecorridoListView(ListView):
    model = Recorrido
    template_name = 'public/recorridos_list.html'
    context_object_name = 'recorridos'

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(nombre__icontains=query)
        return queryset

class RecorridoDetailView(DetailView):
    model = Recorrido
    template_name = 'public/recorrido_detail.html'
    context_object_name = 'recorrido'

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

def nosotros(request):
    return render(request, 'public/nosotros.html') # Temporal