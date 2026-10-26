from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ValidationError
from django.db.models import Prefetch, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView

from .models import (
    Atractivo, Autobus, Chofer, Parada, Recorrido,
    RecorridoParada, Reparacion, Viaje,
)


# ---------------------------------------------------------------
# Mixins reutilizables (herencia / POO)
# ---------------------------------------------------------------
class BusquedaMixin:
    """Filtra el queryset con el parámetro GET ?q=, buscando en `campos_busqueda`."""
    campos_busqueda = ()

    def get_queryset(self):
        queryset = super().get_queryset()
        texto = self.request.GET.get("q", "").strip()
        if texto and self.campos_busqueda:
            filtro = Q()
            for campo in self.campos_busqueda:
                filtro |= Q(**{f"{campo}__icontains": texto})
            queryset = queryset.filter(filtro).distinct()
        return queryset


class StaffRequiredMixin(UserPassesTestMixin):
    """Solo usuarios activos con is_staff acceden; el resto va al login del panel."""
    login_url = reverse_lazy("admin_login")

    def test_func(self):
        usuario = self.request.user
        return usuario.is_active and usuario.is_staff

    def handle_no_permission(self):
        return redirect(self.login_url)


# ---------------------------------------------------------------
# Parte pública
# ---------------------------------------------------------------
class HomeView(TemplateView):
    template_name = "public/home.html"


class NosotrosView(TemplateView):
    template_name = "public/nosotros.html"


def _paradas_ordenadas():
    return Prefetch(
        "paradas_asociadas",
        queryset=RecorridoParada.objects.select_related("parada").order_by("orden"),
    )


class RecorridoListView(BusquedaMixin, ListView):
    model = Recorrido
    template_name = "public/recorridos_list.html"
    context_object_name = "recorridos"
    campos_busqueda = ("color", "descripcion", "paradas_asociadas__parada__nombre",
                       "paradas_asociadas__parada__direccion")

    def get_queryset(self):
        return super().get_queryset().prefetch_related(_paradas_ordenadas())


class RecorridoDetailView(DetailView):
    model = Recorrido
    template_name = "public/recorrido_detail.html"
    context_object_name = "recorrido"

    def get_queryset(self):
        return super().get_queryset().prefetch_related(_paradas_ordenadas())


class ParadaListView(BusquedaMixin, ListView):
    model = Parada
    template_name = "public/paradas_list.html"
    context_object_name = "paradas"
    campos_busqueda = ("nombre", "direccion", "descripcion")


class ParadaDetailView(DetailView):
    model = Parada
    template_name = "public/parada_detail.html"
    context_object_name = "parada"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("atractivos")


class AtractivoListView(BusquedaMixin, ListView):
    model = Atractivo
    template_name = "public/atractivos_list.html"
    context_object_name = "atractivos"
    campos_busqueda = ("nombre", "descripcion")

    def get_queryset(self):
        return super().get_queryset().order_by("-calificacion", "nombre")


class AtractivoDetailView(DetailView):
    model = Atractivo
    template_name = "public/atractivo_detail.html"
    context_object_name = "atractivo"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("paradas")


# ---------------------------------------------------------------
# Panel administrativo
# ---------------------------------------------------------------
class PanelAuthenticationForm(AuthenticationForm):
    """Igual que el formulario de Django, pero solo deja entrar a usuarios is_staff."""

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise ValidationError("Usuario o contraseña incorrectos.", code="no_staff")


class PanelLoginView(LoginView):
    template_name = "admin_panel/login.html"
    authentication_form = PanelAuthenticationForm
    next_page = reverse_lazy("admin_dashboard")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect("admin_dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        messages.error(self.request, "Usuario o contraseña incorrectos.")
        return super().form_invalid(form)


class PanelLogoutView(LogoutView):
    """Cierra sesión (solo por POST) y vuelve al login del panel."""
    next_page = reverse_lazy("admin_login")


class DashboardView(StaffRequiredMixin, TemplateView):
    template_name = "admin_panel/dashboard.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto.update(
            total_buses=Autobus.objects.count(),
            total_choferes=Chofer.objects.count(),
            total_recorridos=Recorrido.objects.count(),
            total_viajes=Viaje.objects.count(),
            reparaciones_abiertas=Reparacion.objects.filter(fecha_fin__isnull=True).count(),
        )
        return contexto