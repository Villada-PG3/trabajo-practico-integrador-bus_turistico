from .roles import puede, roles_de


def permisos_panel(request):
    """Datos de rol y permisos disponibles en todas las plantillas."""
    usuario = request.user

    return {
        "roles_usuario": sorted(roles_de(usuario)),
        "permisos": {
            "flota": puede(usuario, "autobus_list"),
            "contenido": puede(usuario, "recorrido_admin_list"),
            "ver_viajes": puede(usuario, "viaje_list"),
            "programar_viajes": puede(usuario, "viaje_create"),
            "operar_viajes": puede(usuario, "viaje_iniciar"),
            "ver_reporte": puede(usuario, "reporte_diario"),
        },
    }