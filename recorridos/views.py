
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ValidationError
from django.db.models import Prefetch, Q
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    UpdateView,
    DetailView,
    ListView,
    TemplateView,
)

from .forms_choferes import ChoferForm
from .forms import AutobusForm
from .forms_viajes import ViajeForm
from .models import (
    Atractivo, Autobus, Chofer, Parada, Recorrido,
    RecorridoParada, Reparacion, Viaje,
)



# ---------------------------------------------------------------
# Mixins reutilizables
# ---------------------------------------------------------------

class BusquedaMixin:
    """Filtra los resultados utilizando el parametro GET ?q=."""

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
    """Permite acceder solamente al personal autorizado."""

    login_url = reverse_lazy("admin_login")

    def test_func(self):
        usuario = self.request.user
        return usuario.is_active and usuario.is_staff

    def handle_no_permission(self):
        return redirect(self.login_url)


# ---------------------------------------------------------------
# Parte publica
# ---------------------------------------------------------------

class HomeView(TemplateView):
    template_name = "public/home.html"


class NosotrosView(TemplateView):
    template_name = "public/nosotros.html"


def _paradas_ordenadas():
    return Prefetch(
        "paradas_asociadas",
        queryset=RecorridoParada.objects.select_related(
            "parada"
        ).order_by("orden"),
    )


class RecorridoListView(BusquedaMixin, ListView):
    model = Recorrido
    template_name = "public/recorridos_list.html"
    context_object_name = "recorridos"
    campos_busqueda = (
        "color",
        "descripcion",
        "paradas_asociadas__parada__nombre",
        "paradas_asociadas__parada__direccion",
    )

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            _paradas_ordenadas()
        )


class RecorridoDetailView(DetailView):
    model = Recorrido
    template_name = "public/recorrido_detail.html"
    context_object_name = "recorrido"

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            _paradas_ordenadas()
        )


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
        return super().get_queryset().prefetch_related(
            "atractivos"
        )


class AtractivoListView(BusquedaMixin, ListView):
    model = Atractivo
    template_name = "public/atractivos_list.html"
    context_object_name = "atractivos"
    campos_busqueda = ("nombre", "descripcion")

    def get_queryset(self):
        return super().get_queryset().order_by(
            "-calificacion", "nombre"
        )


class AtractivoDetailView(DetailView):
    model = Atractivo
    template_name = "public/atractivo_detail.html"
    context_object_name = "atractivo"

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            "paradas"
        )


# ---------------------------------------------------------------
# Panel administrativo
# ---------------------------------------------------------------

class PanelAuthenticationForm(AuthenticationForm):
    """Permite iniciar sesion solamente a usuarios staff."""

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)

        if not user.is_staff:
            raise ValidationError(
                "Usuario o contraseña incorrectos.",
                code="no_staff",
            )


class PanelLoginView(LoginView):
    template_name = "admin_panel/login.html"
    authentication_form = PanelAuthenticationForm
    next_page = reverse_lazy("admin_dashboard")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect("admin_dashboard")

        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Usuario o contraseña incorrectos."
        )
        return super().form_invalid(form)


class PanelLogoutView(LogoutView):
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
            reparaciones_abiertas=Reparacion.objects.filter(
                fecha_fin__isnull=True
            ).count(),
        )

        return contexto


# ---------------------------------------------------------------
# Gestion de autobuses
# ---------------------------------------------------------------

class AutobusCreateView(StaffRequiredMixin, CreateView):
    model = Autobus
    form_class = AutobusForm
    template_name = "admin_panel/autobus_form.html"
    success_url = reverse_lazy("admin_dashboard")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Autobús registrado correctamente."
        )
        return super().form_valid(form)


class AutobusListView(StaffRequiredMixin, ListView):
    model = Autobus
    template_name = "admin_panel/autobus_list.html"
    context_object_name = "autobuses"

    def get_queryset(self):
        return Autobus.objects.all().order_by("numero_unidad")


class AutobusUpdateView(StaffRequiredMixin, UpdateView):
    model = Autobus
    form_class = AutobusForm
    template_name = "admin_panel/autobus_form.html"
    pk_url_kwarg = "pk"
    success_url = reverse_lazy("autobus_list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Autobús actualizado correctamente."
        )
        return super().form_valid(form)


# ---------------------------------------------------------------
# Gestion de viajes
# ---------------------------------------------------------------

class ViajeListView(StaffRequiredMixin, ListView):
    model = Viaje
    template_name = "admin_panel/viaje_list.html"
    context_object_name = "viajes"

    def get_queryset(self):
        return Viaje.objects.select_related(
            "bus", "chofer", "recorrido"
        ).order_by("-fecha_hora_inicio_programada")


class ViajeIniciarView(StaffRequiredMixin, View):

    def post(self, request, pk):
        viaje = get_object_or_404(Viaje, pk=pk)

        try:
            viaje.iniciar()
            messages.success(
                request,
                "El viaje se inició correctamente."
            )
        except ValidationError as error:
            messages.error(
                request,
                "; ".join(error.messages)
            )

        return redirect("viaje_list")


class ViajeFinalizarView(StaffRequiredMixin, View):

    def post(self, request, pk):
        viaje = get_object_or_404(Viaje, pk=pk)

        try:
            viaje.finalizar()
            messages.success(
                request,
                "El viaje finalizó correctamente."
            )
        except ValidationError as error:
            messages.error(
                request,
                "; ".join(error.messages)
            )

        return redirect("viaje_list")


class ViajeCreateView(StaffRequiredMixin, CreateView):
    model = Viaje
    form_class = ViajeForm
    template_name = "admin_panel/viaje_form.html"
    success_url = reverse_lazy("viaje_list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Viaje programado correctamente."
        )
        return super().form_valid(form)



# ---------------------------------------------------------------
# Gestion de choferes
# ---------------------------------------------------------------

class ChoferListView(StaffRequiredMixin, ListView):
    model = Chofer
    template_name = "admin_panel/chofer_list.html"
    context_object_name = "choferes"

    def get_queryset(self):
        return Chofer.objects.all().order_by("apellido", "nombre")


class ChoferCreateView(StaffRequiredMixin, CreateView):
    model = Chofer
    form_class = ChoferForm
    template_name = "admin_panel/chofer_form.html"
    success_url = reverse_lazy("chofer_list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Chofer registrado correctamente."
        )
        return super().form_valid(form)


class ChoferUpdateView(StaffRequiredMixin, UpdateView):
    model = Chofer
    form_class = ChoferForm
    template_name = "admin_panel/chofer_form.html"
    success_url = reverse_lazy("chofer_list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Chofer actualizado correctamente."
        )
        return super().form_valid(form)
