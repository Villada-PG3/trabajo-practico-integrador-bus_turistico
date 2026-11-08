"""
Roles del panel de administracion.

Cada rol es un grupo de Django (los grupos se crean solos al ejecutar
`python manage.py migrate`). El superusuario siempre es Administrador.

La matriz PERMISOS indica que roles pueden entrar a cada pantalla del
panel, identificada por el nombre de su URL. Si una URL no figura en la
matriz, solo puede entrar el Administrador.
"""
from .models import Viaje

ADMINISTRADOR = "Administrador"
ENCARGADO = "Encargado de Operaciones"
CHOFER = "Chofer"
GERENTE = "Gerente de Operaciones"

ROLES = (ADMINISTRADOR, ENCARGADO, CHOFER, GERENTE)


# ---------------------------------------------------------------
# Matriz de permisos
# ---------------------------------------------------------------
PERMISOS = {}


def _permitir(roles, *nombres_url):
    for nombre in nombres_url:
        PERMISOS[nombre] = frozenset(roles)


# Pantalla principal: todos los roles
_permitir(ROLES, "admin_dashboard")

# Flota: autobuses, choferes y reparaciones
_permitir(
    {ADMINISTRADOR, ENCARGADO},
    "autobus_list", "autobus_create", "autobus_update",
    "chofer_list", "chofer_create", "chofer_update",
    "reparacion_list", "reparacion_create", "reparacion_finalizar",
)

# Contenido turistico: recorridos, paradas y atractivos
_permitir(
    {ADMINISTRADOR},
    "recorrido_admin_list", "recorrido_create", "recorrido_update",
    "parada_admin_list", "parada_create", "parada_update",
    "recorrido_parada_list", "recorrido_parada_create",
    "recorrido_parada_update", "recorrido_parada_delete",
    "atractivo_admin_list", "atractivo_create", "atractivo_update",
    "parada_atractivo_list", "parada_atractivo_create",
    "parada_atractivo_update", "parada_atractivo_delete",
)

# Viajes: todos los roles los consultan y ven el ticket
_permitir(ROLES, "viaje_list", "viaje_ticket")
# Programar viajes (define la dupla bus-chofer y el horario)
_permitir({ADMINISTRADOR, ENCARGADO}, "viaje_create")
# Iniciar y finalizar viajes
_permitir({ADMINISTRADOR, CHOFER}, "viaje_iniciar", "viaje_finalizar")

# Reporte diario
_permitir({ADMINISTRADOR, GERENTE}, "reporte_diario")


# ---------------------------------------------------------------
# Funciones de consulta
# ---------------------------------------------------------------
def roles_de(usuario):
    """Devuelve el conjunto de roles del usuario (vacio si no tiene ninguno)."""
    if not (usuario.is_authenticated and usuario.is_active):
        return frozenset()

    if not hasattr(usuario, "_roles_cache"):
        roles = set(
            usuario.groups.filter(name__in=ROLES).values_list("name", flat=True)
        )
        if usuario.is_superuser:
            roles.add(ADMINISTRADOR)
        usuario._roles_cache = frozenset(roles)

    return usuario._roles_cache


def puede(usuario, nombre_url):
    """True si alguno de los roles del usuario puede entrar a esa URL."""
    permitidos = PERMISOS.get(nombre_url, frozenset({ADMINISTRADOR}))
    return bool(roles_de(usuario) & permitidos)


def viajes_visibles(usuario):
    """
    Viajes que el usuario puede ver. El Administrador, el Encargado y el
    Gerente ven todos; el Chofer solo los que tiene asignados.
    """
    viajes = Viaje.objects.select_related("bus", "chofer", "recorrido")

    if roles_de(usuario) & {ADMINISTRADOR, ENCARGADO, GERENTE}:
        return viajes

    return viajes.filter(chofer__usuario=usuario)