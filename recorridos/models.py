from django.db import models


class Chofer(models.Model):
    legajo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)

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

    def __str__(self):
        return f"Unidad {self.numero_unidad} ({self.patente})"

    class Meta:
        verbose_name = "Autobús"
        verbose_name_plural = "Autobuses"


class Recorrido(models.Model):
    id_recorrido = models.AutoField(primary_key=True)
    color = models.CharField(max_length=30)
    frecuencia = models.IntegerField(help_text="Frecuencia en minutos")
    hora_inicio = models.TimeField()
    hora_finalizacion = models.TimeField()
    duracion_aproximada = models.IntegerField(help_text="Duración en minutos")

    def __str__(self):
        return f"Recorrido {self.color}"

    class Meta:
        verbose_name = "Recorrido"
        verbose_name_plural = "Recorridos"


class Parada(models.Model):
    id_parada = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    direccion = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    foto = models.ImageField(upload_to="paradas/", blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Parada"
        verbose_name_plural = "Paradas"


class Atractivo(models.Model):
    id_atractivo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    calificacion = models.IntegerField()

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Atractivo"
        verbose_name_plural = "Atractivos"


class RecorridoParada(models.Model):
    id_recorrido_parada = models.AutoField(primary_key=True)
    id_recorrido = models.ForeignKey(Recorrido, on_delete=models.CASCADE, db_column="id_recorrido")
    id_parada = models.ForeignKey(Parada, on_delete=models.CASCADE, db_column="id_parada")
    orden = models.IntegerField()

    def __str__(self):
        return f"{self.id_recorrido} - {self.id_parada} (orden {self.orden})"

    class Meta:
        verbose_name = "Recorrido-Parada"
        verbose_name_plural = "Recorrido-Paradas"
        ordering = ["id_recorrido", "orden"]


class ParadaAtractivo(models.Model):
    id_parada_atractivo = models.AutoField(primary_key=True)
    id_parada = models.ForeignKey(Parada, on_delete=models.CASCADE, db_column="id_parada")
    id_atractivo = models.ForeignKey(Atractivo, on_delete=models.CASCADE, db_column="id_atractivo")

    def __str__(self):
        return f"{self.id_parada} - {self.id_atractivo}"

    class Meta:
        verbose_name = "Parada-Atractivo"
        verbose_name_plural = "Parada-Atractivos"


class Viaje(models.Model):
    id_viaje = models.AutoField(primary_key=True)
    fecha_hora_inicio_programada = models.DateTimeField()
    fecha_hora_inicio_real = models.DateTimeField(blank=True, null=True)
    fecha_hora_fin_real = models.DateTimeField(blank=True, null=True)
    id_bus = models.ForeignKey(Autobus, on_delete=models.CASCADE, db_column="id_bus")
    legajo_chofer = models.ForeignKey(Chofer, on_delete=models.CASCADE, db_column="legajo_chofer")
    id_recorrido = models.ForeignKey(Recorrido, on_delete=models.CASCADE, db_column="id_recorrido")

    def __str__(self):
        return f"Viaje {self.id_viaje} - {self.id_recorrido}"

    class Meta:
        verbose_name = "Viaje"
        verbose_name_plural = "Viajes"


class Reparacion(models.Model):
    id_reparacion = models.AutoField(primary_key=True)
    id_bus = models.ForeignKey(Autobus, on_delete=models.CASCADE, db_column="id_bus", related_name="reparaciones")
    descripcion = models.TextField()
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Reparación {self.id_reparacion} - {self.id_bus}"

    class Meta:
        verbose_name = "Reparación"
        verbose_name_plural = "Reparaciones"