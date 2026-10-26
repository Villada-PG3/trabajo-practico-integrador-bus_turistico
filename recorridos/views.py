from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, TemplateView

# Importación de modelos del dominio
from .models import Recorrido, Parada, Atractivo


# --- VISTAS GENERALES Y ESTÁTICAS (CBV) ---

class HomeView(TemplateView):
    template_name = 'public/home.html'


class NosotrosView(TemplateView):
    """
    Vista basada en clases para la sección Institucional / Nosotros.
    Renderiza la plantilla creada por tu compañero en 'templates/public/nosotros.html'.
    """
    template_name = 'public/nosotros.html'


# --- MÓDULO DE RECORRIDOS (CBV) ---

class RecorridoListView(ListView):
    model = Recorrido
    template_name = 'public/recorridos_list.html'
    context_object_name = 'recorridos'
    ordering = ['id_recorrido']  # Se define el orden por defecto para evitar listas desordenadas

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


# --- MÓDULO DE PARADAS (CBV) ---

class ParadaListView(ListView):
    model = Parada
    template_name = 'public/paradas_list.html'
    context_object_name = 'paradas'
    paginate_by = 6
    ordering = ['id_parada']  

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(nombre_icontains=query) | queryset.filter(direccion_icontains=query)
        return queryset


class ParadaDetailView(DetailView):
    model = Parada
    template_name = 'public/parada_detail.html'
    context_object_name = 'parada'


# --- MÓDULO DE ATRACTIVOS TURÍSTICOS (CBV) ---

class AtractivoListView(ListView):
    model = Atractivo
    template_name = 'public/atractivos_list.html'
    context_object_name = 'atractivos'
    paginate_by = 6
    ordering = ['id_atractivo']  # Soluciona UnorderedObjectListWarning al paginar

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(nombre_icontains=query) | queryset.filter(descripcion_icontains=query)
        return queryset


class AtractivoDetailView(DetailView):
    model = Atractivo
    template_name = 'public/atractivo_detail.html'
    context_object_name = 'atractivo'


# --- PANEL ADMINISTRATIVO (DUEÑO) ---

def admin_login(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        usuario = request.POST.get('username')
        clave = request.POST.get('password')
        
        user = authenticate(request, username=usuario, password=clave)
        
        if user is not None:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'admin_panel/login.html')


@login_required(login_url='admin_login')
def admin_dashboard(request):
    return render(request, 'admin_panel/dashboard.html')


def admin_logout(request):
    logout(request)
    return redirect('admin_login')