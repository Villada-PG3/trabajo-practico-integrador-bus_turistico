from django.contrib import admin
from .models import (
    Chofer, Autobus, Recorrido, Parada, Atractivo,
    RecorridoParada, ParadaAtractivo, Viaje, Reparacion,
)


@admin.register(Chofer)
class ChoferAdmin(admin.ModelAdmin):
    list_display = ("legajo", "nombre", "apellido")
    search_fields = ("nombre", "apellido")


@admin.register(Autobus)
class AutobusAdmin(admin.ModelAdmin):
    list_display = ("id_bus", "numero_unidad", "patente", "estado", "fecha_compra")
    list_filter = ("estado",)
    search_fields = ("patente", "numero_unidad")


@admin.register(Recorrido)
class RecorridoAdmin(admin.ModelAdmin):
    list_display = ("id_recorrido", "color", "frecuencia", "hora_inicio", "hora_finalizacion", "duracion_aproximada")


@admin.register(Parada)
class ParadaAdmin(admin.ModelAdmin):
    list_display = ("id_parada", "nombre", "direccion")
    search_fields = ("nombre", "direccion")


@admin.register(Atractivo)
class AtractivoAdmin(admin.ModelAdmin):
    list_display = ("id_atractivo", "nombre", "calificacion")
    list_filter = ("calificacion",)


@admin.register(RecorridoParada)
class RecorridoParadaAdmin(admin.ModelAdmin):
    list_display = ("id_recorrido_parada", "id_recorrido", "id_parada", "orden")
    list_filter = ("id_recorrido",)


@admin.register(ParadaAtractivo)
class ParadaAtractivoAdmin(admin.ModelAdmin):
    list_display = ("id_parada_atractivo", "id_parada", "id_atractivo")


@admin.register(Viaje)
class ViajeAdmin(admin.ModelAdmin):
    list_display = (
        "id_viaje", "id_recorrido", "id_bus", "legajo_chofer",
        "fecha_hora_inicio_programada", "fecha_hora_inicio_real", "fecha_hora_fin_real",
    )
    list_filter = ("id_recorrido", "id_bus")


@admin.register(Reparacion)
class ReparacionAdmin(admin.ModelAdmin):
    list_display = ("id_reparacion", "id_bus", "fecha_inicio", "fecha_fin")
    list_filter = ("id_bus",)