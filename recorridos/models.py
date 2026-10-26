from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone


class Chofer(models.Model):
    legajo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"

    class Meta:
        verbose_name = "Chofer"
        verbose_name_plural = "Choferes"


class Autobus(models.Model):
    id_bus = models.AutoField(primary_key=True)
    patente = models.CharField(max_length=10)
    numero_unidad = models.IntegerField()
    fecha_compra = models.DateField()
    estado = models.CharField(max_length=50)

    @property
    def en_reparacion(self):
        """True si el bus tiene alguna reparación sin fecha de fin."""
        return bool(self.pk) and self.reparaciones.filter(fecha_fin__isnull=True).exists()

    def __str__(self):
        return f"Unidad {self.numero_unidad} ({self.patente})"

    class Meta:
        verbose_name = "Autobús"
        verbose_name_plural = "Autobuses"


class Recorrido(models.Model):
    FRECUENCIAS = [
        (20, "Cada 20 minutos"),
        (30, "Cada 30 minutos"),
    ]

    id_recorrido = models.AutoField(primary_key=True)
    color = models.CharField(
        max_length=30, unique=True,
        help_text="Nombre del color que identifica al recorrido (ej. Verde)",
    )
    color_hex = models.CharField(
        max_length=7, default="#2563eb",
        validators=[RegexValidator(r"^#[0-9a-fA-F]{6}$", "Usá el formato #RRGGBB (ej. #16a34a).")],
        help_text="Color en formato hexadecimal, ej. #16a34a",
    )
    descripcion = models.TextField(blank=True)
    frecuencia_minutos = models.PositiveSmallIntegerField(
        choices=FRECUENCIAS, default=30, help_text="Cada cuántos minutos pasa un bus",
    )
    hora_inicio = models.TimeField(help_text="Salida del primer bus desde la primera parada")
    hora_fin = models.TimeField(help_text="Llegada aproximada del último bus a la última parada")
    duracion_aproximada = models.PositiveIntegerField(help_text="Duración del circuito completo, en minutos")

    @property
    def nombre(self):
        return f"Recorrido {self.color}"

    def cantidad_paradas(self):
        return self.paradas_asociadas.count()

    def clean(self):
        if self.hora_inicio and self.hora_fin and self.hora_fin <= self.hora_inicio:
            raise ValidationError({"hora_fin": "La hora de finalización debe ser posterior a la de inicio."})

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Recorrido"
        verbose_name_plural = "Recorridos"
        ordering = ["color"]


class Atractivo(models.Model):
    id_atractivo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to="atractivos/", blank=True, null=True)
    calificacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Calificación en estrellas (1 a 5)",
    )

    @property
    def calificacion_estrellas(self):
        return f"{self.calificacion:.1f}"

    @property
    def estrellas(self):
        """Representación visual, ej. ★★★★☆"""
        return "★" * self.calificacion + "☆" * (5 - self.calificacion)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Atractivo"
        verbose_name_plural = "Atractivos"
        ordering = ["nombre"]


class Parada(models.Model):
    id_parada = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    direccion = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to="paradas/", blank=True, null=True)
    atractivos = models.ManyToManyField(
        Atractivo, through="ParadaAtractivo", related_name="paradas", blank=True,
    )

    def cantidad_atractivos(self):
        return self.atractivos.count()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Parada"
        verbose_name_plural = "Paradas"
        ordering = ["nombre"]


class RecorridoParada(models.Model):
    id_recorrido_parada = models.AutoField(primary_key=True)
    recorrido = models.ForeignKey(
        Recorrido, on_delete=models.CASCADE, db_column="id_recorrido", related_name="paradas_asociadas",
    )
    parada = models.ForeignKey(
        Parada, on_delete=models.CASCADE, db_column="id_parada", related_name="recorridos_asociados",
    )
    orden = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.recorrido} - {self.parada} (Orden {self.orden})"

    class Meta:
        verbose_name = "Recorrido-Parada"
        verbose_name_plural = "Recorrido-Paradas"
        ordering = ["recorrido", "orden"]
        constraints = [
            models.UniqueConstraint(fields=["recorrido", "orden"], name="uniq_orden_por_recorrido"),
            models.UniqueConstraint(fields=["recorrido", "parada"], name="uniq_parada_por_recorrido"),
        ]


class ParadaAtractivo(models.Model):
    id_parada_atractivo = models.AutoField(primary_key=True)
    parada = models.ForeignKey(Parada, on_delete=models.CASCADE, db_column="id_parada")
    atractivo = models.ForeignKey(Atractivo, on_delete=models.CASCADE, db_column="id_atractivo")

    def __str__(self):
        return f"{self.parada} - {self.atractivo}"

    class Meta:
        verbose_name = "Parada-Atractivo"
        verbose_name_plural = "Parada-Atractivos"
        constraints = [
            models.UniqueConstraint(fields=["parada", "atractivo"], name="uniq_atractivo_por_parada"),
        ]


class Viaje(models.Model):
    id_viaje = models.AutoField(primary_key=True)
    fecha_hora_inicio_programada = models.DateTimeField()
    fecha_hora_inicio_real = models.DateTimeField(blank=True, null=True)
    fecha_hora_fin_real = models.DateTimeField(blank=True, null=True)
    bus = models.ForeignKey(Autobus, on_delete=models.CASCADE, db_column="id_bus")
    chofer = models.ForeignKey(Chofer, on_delete=models.CASCADE, db_column="legajo_chofer")
    recorrido = models.ForeignKey(Recorrido, on_delete=models.CASCADE, db_column="id_recorrido")

    @property
    def duracion_minutos(self):
        if self.fecha_hora_inicio_real and self.fecha_hora_fin_real:
            return int((self.fecha_hora_fin_real - self.fecha_hora_inicio_real).total_seconds() // 60)
        return None

    @property
    def demora_minutos(self):
        """Minutos entre la hora programada y el inicio real (negativo = salió antes)."""
        if self.fecha_hora_inicio_real:
            return int((self.fecha_hora_inicio_real - self.fecha_hora_inicio_programada).total_seconds() // 60)
        return None

    @property
    def finalizado(self):
        return self.fecha_hora_fin_real is not None

    def iniciar(self):
        if self.fecha_hora_inicio_real:
            raise ValidationError("El viaje ya fue iniciado.")
        self.fecha_hora_inicio_real = timezone.now()
        self.save(update_fields=["fecha_hora_inicio_real"])

    def finalizar(self):
        if not self.fecha_hora_inicio_real:
            raise ValidationError("El viaje todavía no fue iniciado.")
        if self.fecha_hora_fin_real:
            raise ValidationError("El viaje ya fue finalizado.")
        self.fecha_hora_fin_real = timezone.now()
        self.save(update_fields=["fecha_hora_fin_real"])

    def clean(self):
        errores = {}
        if self.fecha_hora_inicio_real and self.fecha_hora_fin_real \
                and self.fecha_hora_fin_real < self.fecha_hora_inicio_real:
            errores["fecha_hora_fin_real"] = "El fin del viaje no puede ser anterior al inicio."
        if self._state.adding and self.bus_id and self.bus.en_reparacion:
            errores["bus"] = "Este autobús está en reparación y no puede asignarse a un viaje."
        if errores:
            raise ValidationError(errores)

    def __str__(self):
        return f"Viaje {self.id_viaje} - {self.recorrido}"

    class Meta:
        verbose_name = "Viaje"
        verbose_name_plural = "Viajes"


class Reparacion(models.Model):
    id_reparacion = models.AutoField(primary_key=True)
    bus = models.ForeignKey(Autobus, on_delete=models.CASCADE, db_column="id_bus", related_name="reparaciones")
    descripcion = models.TextField()
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Reparación {self.id_reparacion} - {self.bus}"

    class Meta:
        verbose_name = "Reparación"
        verbose_name_plural = "Reparaciones"