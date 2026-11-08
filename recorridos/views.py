import datetime
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ValidationError
from django.db.models import (
    Avg, Count, DurationField, ExpressionWrapper, F, Prefetch, Q,
)
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
from .roles import puede, roles_de, viajes_visibles
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


class RolRequeridoMixin(UserPassesTestMixin):
    """
    Controla el acceso al panel segun el rol del usuario.

    Cada vista se identifica por el nombre de su URL y la matriz
    PERMISOS (en roles.py) indica que roles pueden entrar.
    """

    login_url = reverse_lazy("admin_login")

    def test_func(self):
        nombre_url = self.request.resolver_match.url_name
        return puede(self.request.user, nombre_url)

    def handle_no_permission(self):
        if roles_de(self.request.user):
            messages.error(
                self.request,
                "No tenés permiso para acceder a esa sección."
            )
            return redirect("admin_dashboard")

        if self.request.user.is_authenticated:
            messages.error(
                self.request,
                "Tu usuario no tiene un rol asignado. "
                "Pedile al administrador que te asigne uno."
            )

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
    """Permite iniciar sesion solamente a usuarios con algun rol."""

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)

        if not roles_de(user):
            raise ValidationError(
                "Usuario o contraseña incorrectos.",
                code="sin_rol",
            )


class PanelLoginView(LoginView):
    template_name = "admin_panel/login.html"
    authentication_form = PanelAuthenticationForm
    next_page = reverse_lazy("admin_dashboard")

    def dispatch(self, request, *args, **kwargs):
            if roles_de(request.user):
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


class DashboardView(RolRequeridoMixin, TemplateView):
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

class AutobusCreateView(RolRequeridoMixin, CreateView):
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


class AutobusListView(RolRequeridoMixin, ListView):
    model = Autobus
    template_name = "admin_panel/autobus_list.html"
    context_object_name = "autobuses"

    def get_queryset(self):
        return Autobus.objects.all().order_by("numero_unidad")


class AutobusUpdateView(RolRequeridoMixin, UpdateView):
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

class ViajeListView(RolRequeridoMixin, ListView):
    model = Viaje
    template_name = "admin_panel/viaje_list.html"
    context_object_name = "viajes"

    def get_queryset(self):
        return viajes_visibles(self.request.user).order_by(
            "-fecha_hora_inicio_programada"
        )


class ViajeIniciarView(RolRequeridoMixin, View):

    def post(self, request, pk):
        viaje = get_object_or_404(viajes_visibles(request.user), pk=pk)

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


class ViajeFinalizarView(RolRequeridoMixin, View):

    def post(self, request, pk):
        viaje = get_object_or_404(viajes_visibles(request.user), pk=pk)

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

        # Al finalizar el viaje se emite el ticket
        return redirect("viaje_ticket", pk=viaje.pk)


class ViajeTicketView(RolRequeridoMixin, DetailView):
    """Ticket del viaje: solo se puede ver cuando el viaje ya finalizó."""
    model = Viaje
    template_name = "admin_panel/viaje_ticket.html"
    context_object_name = "viaje"

    def get_queryset(self):
        return viajes_visibles(self.request.user)

    def get(self, request, *args, **kwargs):
        viaje = self.get_object()
        if not viaje.finalizado:
            messages.error(
                request,
                "El ticket solo está disponible cuando el viaje finalizó."
            )
            return redirect("viaje_list")
        return super().get(request, *args, **kwargs)

class ReporteDiarioView(RolRequeridoMixin, TemplateView):
    """
    Reporte diario de viajes para el Gerente de Operaciones.

    Muestra los viajes programados para el dia elegido (?fecha=AAAA-MM-DD,
    por defecto hoy) con su duracion y la demora de inicio, y los
    promedios diarios de ambos valores. Los promedios se calculan en la
    base de datos con una sola consulta.
    """
    template_name = "admin_panel/reporte_diario.html"

    def get_fecha(self):
        texto = self.request.GET.get("fecha")
        if texto:
            try:
                return datetime.date.fromisoformat(texto)
            except ValueError:
                messages.error(
                    self.request,
                    "La fecha ingresada no es válida. Se muestra el día de hoy."
                )
        return timezone.localdate()

    @staticmethod
    def _a_minutos(intervalo):
        if intervalo is None:
            return None
        return round(intervalo.total_seconds() / 60, 1)

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        fecha = self.get_fecha()

        dia = datetime.timedelta(days=1)
        inicio_dia = timezone.make_aware(
            datetime.datetime.combine(fecha, datetime.time.min)
        )
        fin_dia = timezone.make_aware(
            datetime.datetime.combine(fecha + dia, datetime.time.min)
        )

        viajes = (
            Viaje.objects
            .filter(
                fecha_hora_inicio_programada__gte=inicio_dia,
                fecha_hora_inicio_programada__lt=fin_dia,
            )
            .select_related("bus", "chofer", "recorrido")
            .order_by("fecha_hora_inicio_programada")
        )

        duracion = ExpressionWrapper(
            F("fecha_hora_fin_real") - F("fecha_hora_inicio_real"),
            output_field=DurationField(),
        )
        demora = ExpressionWrapper(
            F("fecha_hora_inicio_real") - F("fecha_hora_inicio_programada"),
            output_field=DurationField(),
        )

        resumen = viajes.aggregate(
            total=Count("pk"),
            finalizados=Count("pk", filter=Q(estado="FINALIZADO")),
            en_curso=Count("pk", filter=Q(estado="EN_CURSO")),
            programados=Count("pk", filter=Q(estado="PROGRAMADO")),
            cancelados=Count("pk", filter=Q(estado="CANCELADO")),
            promedio_duracion=Avg(
                duracion,
                filter=Q(
                    fecha_hora_inicio_real__isnull=False,
                    fecha_hora_fin_real__isnull=False,
                ),
            ),
            promedio_demora=Avg(
                demora, filter=Q(fecha_hora_inicio_real__isnull=False),
            ),
        )
        resumen["promedio_duracion"] = self._a_minutos(resumen["promedio_duracion"])
        resumen["promedio_demora"] = self._a_minutos(resumen["promedio_demora"])

        contexto.update(
            fecha=fecha,
            viajes=viajes,
            resumen=resumen,
            dia_anterior=(fecha - dia).isoformat(),
            dia_siguiente=(fecha + dia).isoformat(),
            es_hoy=(fecha == timezone.localdate()),
        )
        return contexto

class ViajeCreateView(RolRequeridoMixin, CreateView):
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

class ChoferListView(RolRequeridoMixin, ListView):
    model = Chofer
    template_name = "admin_panel/chofer_list.html"
    context_object_name = "choferes"

    def get_queryset(self):
        return Chofer.objects.all().order_by("apellido", "nombre")


class ChoferCreateView(RolRequeridoMixin, CreateView):
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


class ChoferUpdateView(RolRequeridoMixin, UpdateView):
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

class ReparacionListView(RolRequeridoMixin, ListView):
    model = Reparacion
    template_name = "admin_panel/reparacion_list.html"
    context_object_name = "reparaciones"

    def get_queryset(self):
        return Reparacion.objects.select_related(
            "bus"
        ).order_by("-fecha_inicio")


class ReparacionCreateView(RolRequeridoMixin, CreateView):
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

class ReparacionFinalizarView(RolRequeridoMixin, View):

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

class RecorridoListAdminView(RolRequeridoMixin, ListView):
    model = Recorrido
    template_name = "admin_panel/recorrido_list.html"
    context_object_name = "recorridos"

    def get_queryset(self):
        return Recorrido.objects.all().order_by("color")


class RecorridoCreateView(RolRequeridoMixin, CreateView):
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


class RecorridoUpdateView(RolRequeridoMixin, UpdateView):
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

class ParadaListAdminView(RolRequeridoMixin, ListView):
    model = Parada
    template_name = "admin_panel/parada_list.html"
    context_object_name = "paradas"

    def get_queryset(self):
        return Parada.objects.all().order_by("nombre")


class ParadaCreateView(RolRequeridoMixin, CreateView):
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


class ParadaUpdateView(RolRequeridoMixin, UpdateView):
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


class RecorridoParadaCreateView(RolRequeridoMixin, CreateView):
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

class RecorridoParadaListView(RolRequeridoMixin, ListView):
    model = RecorridoParada
    template_name = "admin_panel/recorrido_parada_list.html"
    context_object_name = "asignaciones"

    def get_queryset(self):
        return RecorridoParada.objects.select_related(
            "recorrido", "parada"
        ).order_by("recorrido__color", "orden")


class RecorridoParadaUpdateView(RolRequeridoMixin, UpdateView):
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


class RecorridoParadaDeleteView(RolRequeridoMixin, DeleteView):
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

class AtractivoListAdminView(RolRequeridoMixin, ListView):
    model = Atractivo
    template_name = "admin_panel/atractivo_list.html"
    context_object_name = "atractivos"

    def get_queryset(self):
        return Atractivo.objects.all().order_by("nombre")


class AtractivoCreateView(RolRequeridoMixin, CreateView):
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


class AtractivoUpdateView(RolRequeridoMixin, UpdateView):
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


class ParadaAtractivoCreateView(RolRequeridoMixin, CreateView):
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

class ParadaAtractivoListView(RolRequeridoMixin, ListView):
    model = ParadaAtractivo
    template_name = "admin_panel/parada_atractivo_list.html"
    context_object_name = "asociaciones"

    def get_queryset(self):
        return ParadaAtractivo.objects.select_related(
            "parada", "atractivo"
        ).order_by("parada__nombre", "atractivo__nombre")


# Editar una asociacion existente

class ParadaAtractivoUpdateView(RolRequeridoMixin, UpdateView):
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

class ParadaAtractivoDeleteView(RolRequeridoMixin, DeleteView):
    model = ParadaAtractivo
    template_name = "admin_panel/parada_atractivo_confirm_delete.html"
    success_url = reverse_lazy("parada_atractivo_list")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Asociación eliminada correctamente."
        )
        return super().form_valid(form)
