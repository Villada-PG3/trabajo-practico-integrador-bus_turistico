from django.contrib import admin
from .models import (
    Chofer, Autobus, Recorrido, Parada, Atractivo,
    RecorridoParada, ParadaAtractivo, Viaje, Reparacion,
)


class RecorridoParadaInline(admin.TabularInline):
    model = RecorridoParada
    extra = 1
    ordering = ("orden",)


class ParadaAtractivoInline(admin.TabularInline):
    model = ParadaAtractivo
    extra = 1


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
    list_display = ("id_recorrido", "color", "frecuencia_minutos", "hora_inicio", "hora_fin", "duracion_aproximada")
    inlines = [RecorridoParadaInline]


@admin.register(Parada)
class ParadaAdmin(admin.ModelAdmin):
    list_display = ("id_parada", "nombre", "direccion")
    search_fields = ("nombre", "direccion")
    inlines = [ParadaAtractivoInline]


@admin.register(Atractivo)
class AtractivoAdmin(admin.ModelAdmin):
    list_display = ("id_atractivo", "nombre", "calificacion")
    list_filter = ("calificacion",)
    search_fields = ("nombre",)


@admin.register(RecorridoParada)
class RecorridoParadaAdmin(admin.ModelAdmin):
    list_display = ("id_recorrido_parada", "recorrido", "parada", "orden")
    list_filter = ("recorrido",)


@admin.register(ParadaAtractivo)
class ParadaAtractivoAdmin(admin.ModelAdmin):
    list_display = ("id_parada_atractivo", "parada", "atractivo")


@admin.register(Viaje)
class ViajeAdmin(admin.ModelAdmin):
    list_display = (
        "id_viaje", "recorrido", "bus", "chofer",
        "fecha_hora_inicio_programada", "fecha_hora_inicio_real", "fecha_hora_fin_real",
    )
    list_filter = ("recorrido", "bus")


@admin.register(Reparacion)
class ReparacionAdmin(admin.ModelAdmin):
    list_display = ("id_reparacion", "bus", "fecha_inicio", "fecha_fin")
    list_filter = ("bus",)