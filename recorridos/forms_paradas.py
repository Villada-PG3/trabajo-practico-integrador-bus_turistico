
from django import forms

from .models import Parada, RecorridoParada


class ParadaForm(forms.ModelForm):

    class Meta:
        model = Parada

        fields = [
            "nombre",
            "direccion",
            "descripcion",
            "imagen",
        ]

        labels = {
            "nombre": "Nombre de la parada",
            "direccion": "Dirección",
            "descripcion": "Descripción",
            "imagen": "Imagen de la parada",
        }

        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "direccion": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),
            "imagen": forms.ClearableFileInput(
                attrs={"class": "form-control"}
            ),
        }


class RecorridoParadaForm(forms.ModelForm):

    class Meta:
        model = RecorridoParada

        fields = [
            "recorrido",
            "parada",
            "orden",
        ]

        labels = {
            "recorrido": "Recorrido turístico",
            "parada": "Parada",
            "orden": "Orden de la parada",
        }

        widgets = {
            "recorrido": forms.Select(
                attrs={"class": "form-select"}
            ),
            "parada": forms.Select(
                attrs={"class": "form-select"}
            ),
            "orden": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        recorrido = cleaned_data.get("recorrido")
        parada = cleaned_data.get("parada")
        orden = cleaned_data.get("orden")

        if not recorrido:
            return cleaned_data

        asignaciones = RecorridoParada.objects.filter(
            recorrido=recorrido
        )

        if self.instance.pk:
            asignaciones = asignaciones.exclude(pk=self.instance.pk)

        if parada and asignaciones.filter(parada=parada).exists():
            self.add_error(
                "parada",
                "Esta parada ya pertenece al recorrido seleccionado."
            )

        if orden is not None and asignaciones.filter(orden=orden).exists():
            self.add_error(
                "orden",
                "Ya existe una parada con ese número de orden en el recorrido."
            )

        return cleaned_data
