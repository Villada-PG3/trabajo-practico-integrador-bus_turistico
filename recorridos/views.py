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
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
)

from .forms_atractivos import AtractivoForm, ParadaAtractivoForm
from .forms_paradas import ParadaForm, RecorridoParadaForm
from .forms_recorridos import RecorridoForm
from .forms_reparaciones import ReparacionForm
from .forms_choferes import ChoferForm
from .forms import AutobusForm
from .forms_viajes import ViajeForm
from .models import (
    Atractivo, Autobus, Chofer, Parada, ParadaAtractivo, Recorrido,
    RecorridoParada, Reparacion, Viaje,
)
from django.utils import timezone


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
            total_paradas=Parada.objects.count(),
            total_atractivos=Atractivo.objects.count(),
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

# ---------------------------------------------------------------
# Gestion de reparaciones
# ---------------------------------------------------------------

class ReparacionListView(StaffRequiredMixin, ListView):
    model = Reparacion
    template_name = "admin_panel/reparacion_list.html"
    context_object_name = "reparaciones"

    def get_queryset(self):
        return Reparacion.objects.select_related(
            "bus"
        ).order_by("-fecha_inicio")


class ReparacionCreateView(StaffRequiredMixin, CreateView):
    model = Reparacion
    form_class = ReparacionForm
    template_name = "admin_panel/reparacion_form.html"
    success_url = reverse_lazy("reparacion_list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Reparación registrada correctamente."
        )
        return super().form_valid(form)

class ReparacionFinalizarView(StaffRequiredMixin, View):

    def post(self, request, pk):
        reparacion = get_object_or_404(Reparacion, pk=pk)

        if reparacion.fecha_fin is not None:
            messages.error(
                request,
                "Esta reparación ya está finalizada."
            )

        elif timezone.now() < reparacion.fecha_inicio:
            messages.error(
                request,
                "No se puede finalizar una reparación antes de su inicio."
            )

        else:
            reparacion.fecha_fin = timezone.now()
            reparacion.save(update_fields=["fecha_fin"])

            messages.success(
                request,
                "Reparación finalizada correctamente."
            )

        return redirect("reparacion_list")

# ---------------------------------------------------------------
# Gestion de recorridos (panel administrativo)
# ---------------------------------------------------------------

class RecorridoListAdminView(StaffRequiredMixin, ListView):
    model = Recorrido
    template_name = "admin_panel/recorrido_list.html"
    context_object_name = "recorridos"

    def get_queryset(self):
        return Recorrido.objects.all().order_by("color")


class RecorridoCreateView(StaffRequiredMixin, CreateView):
    model = Recorrido
    form_class = RecorridoForm
    template_name = "admin_panel/recorrido_form.html"
    success_url = reverse_lazy("recorrido_admin_list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Recorrido registrado correctamente."
        )
        return super().form_valid(form)


class RecorridoUpdateView(StaffRequiredMixin, UpdateView):
    model = Recorrido
    form_class = RecorridoForm
    template_name = "admin_panel/recorrido_form.html"
    success_url = reverse_lazy("recorrido_admin_list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Recorrido actualizado correctamente."
        )
        return super().form_valid(form)


# ---------------------------------------------------------------
# Gestion de paradas (panel administrativo)
# ---------------------------------------------------------------

class ParadaListAdminView(StaffRequiredMixin, ListView):
    model = Parada
    template_name = "admin_panel/parada_list.html"
    context_object_name = "paradas"

    def get_queryset(self):
        return Parada.objects.all().order_by("nombre")


class ParadaCreateView(StaffRequiredMixin, CreateView):
    model = Parada
    form_class = ParadaForm
    template_name = "admin_panel/parada_form.html"
    success_url = reverse_lazy("parada_admin_list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Parada registrada correctamente."
        )
        return super().form_valid(form)


class ParadaUpdateView(StaffRequiredMixin, UpdateView):
    model = Parada
    form_class = ParadaForm
    template_name = "admin_panel/parada_form.html"
    success_url = reverse_lazy("parada_admin_list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Parada actualizada correctamente."
        )
        return super().form_valid(form)


class RecorridoParadaCreateView(StaffRequiredMixin, CreateView):
    model = RecorridoParada
    form_class = RecorridoParadaForm
    template_name = "admin_panel/recorrido_parada_form.html"
    success_url = reverse_lazy("recorrido_admin_list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Parada asignada al recorrido correctamente."
        )
        return super().form_valid(form)

# ---------------------------------------------------------------
# Administracion de paradas asignadas a recorridos
# ---------------------------------------------------------------

class RecorridoParadaListView(StaffRequiredMixin, ListView):
    model = RecorridoParada
    template_name = "admin_panel/recorrido_parada_list.html"
    context_object_name = "asignaciones"

    def get_queryset(self):
        return RecorridoParada.objects.select_related(
            "recorrido", "parada"
        ).order_by("recorrido__color", "orden")


class RecorridoParadaUpdateView(StaffRequiredMixin, UpdateView):
    model = RecorridoParada
    form_class = RecorridoParadaForm
    template_name = "admin_panel/recorrido_parada_form.html"
    success_url = reverse_lazy("recorrido_parada_list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Asignación de parada actualizada correctamente."
        )
        return super().form_valid(form)


class RecorridoParadaDeleteView(StaffRequiredMixin, DeleteView):
    model = RecorridoParada
    template_name = "admin_panel/recorrido_parada_confirm_delete.html"
    success_url = reverse_lazy("recorrido_parada_list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Parada quitada del recorrido correctamente."
        )
        return super().form_valid(form)


# ---------------------------------------------------------------
# Gestion de atractivos turisticos (panel administrativo)
# ---------------------------------------------------------------

class AtractivoListAdminView(StaffRequiredMixin, ListView):
    model = Atractivo
    template_name = "admin_panel/atractivo_list.html"
    context_object_name = "atractivos"

    def get_queryset(self):
        return Atractivo.objects.all().order_by("nombre")


class AtractivoCreateView(StaffRequiredMixin, CreateView):
    model = Atractivo
    form_class = AtractivoForm
    template_name = "admin_panel/atractivo_form.html"
    success_url = reverse_lazy("atractivo_admin_list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Atractivo registrado correctamente."
        )
        return super().form_valid(form)


class AtractivoUpdateView(StaffRequiredMixin, UpdateView):
    model = Atractivo
    form_class = AtractivoForm
    template_name = "admin_panel/atractivo_form.html"
    success_url = reverse_lazy("atractivo_admin_list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Atractivo actualizado correctamente."
        )
        return super().form_valid(form)


class ParadaAtractivoCreateView(StaffRequiredMixin, CreateView):
    model = ParadaAtractivo
    form_class = ParadaAtractivoForm
    template_name = "admin_panel/parada_atractivo_form.html"
    success_url = reverse_lazy("atractivo_admin_list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Atractivo asociado a la parada correctamente."
        )
        return super().form_valid(form)


# Listar asociaciones entre paradas y atractivos

class ParadaAtractivoListView(StaffRequiredMixin, ListView):
    model = ParadaAtractivo
    template_name = "admin_panel/parada_atractivo_list.html"
    context_object_name = "asociaciones"

    def get_queryset(self):
        return ParadaAtractivo.objects.select_related(
            "parada", "atractivo"
        ).order_by("parada__nombre", "atractivo__nombre")


# Editar una asociacion existente

class ParadaAtractivoUpdateView(StaffRequiredMixin, UpdateView):
    model = ParadaAtractivo
    form_class = ParadaAtractivoForm
    template_name = "admin_panel/parada_atractivo_form.html"
    success_url = reverse_lazy("parada_atractivo_list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Asociación actualizada correctamente."
        )
        return super().form_valid(form)


# Quitar una asociacion sin borrar la parada ni el atractivo

class ParadaAtractivoDeleteView(StaffRequiredMixin, DeleteView):
    model = ParadaAtractivo
    template_name = "admin_panel/parada_atractivo_confirm_delete.html"
    success_url = reverse_lazy("parada_atractivo_list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Asociación eliminada correctamente."
        )
        return super().form_valid(form)
