
from django import forms

from .models import Atractivo, ParadaAtractivo


class AtractivoForm(forms.ModelForm):

    class Meta:
        model = Atractivo

        fields = [
            "nombre",
            "descripcion",
            "imagen",
            "calificacion",
        ]

        labels = {
            "nombre": "Nombre del atractivo",
            "descripcion": "Descripción",
            "imagen": "Imagen del atractivo",
            "calificacion": "Calificación",
        }

        widgets = {
            "nombre": forms.TextInput(
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
            "calificacion": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "max": "5",
                }
            ),
        }


class ParadaAtractivoForm(forms.ModelForm):

    class Meta:
        model = ParadaAtractivo

        fields = [
            "parada",
            "atractivo",
            "distancia_metros",
        ]

        labels = {
            "parada": "Parada turística",
            "atractivo": "Atractivo turístico",
            "distancia_metros": "Distancia desde la parada (metros)",
        }

        widgets = {
            "parada": forms.Select(
                attrs={"class": "form-select"}
            ),
            "atractivo": forms.Select(
                attrs={"class": "form-select"}
            ),
            "distancia_metros": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0",
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        parada = cleaned_data.get("parada")
        atractivo = cleaned_data.get("atractivo")

        if parada and atractivo:
            asignaciones = ParadaAtractivo.objects.filter(
                parada=parada,
                atractivo=atractivo,
            )

            if self.instance.pk:
                asignaciones = asignaciones.exclude(
                    pk=self.instance.pk
                )

            if asignaciones.exists():
                self.add_error(
                    "atractivo",
                    "Este atractivo ya está asociado a la parada seleccionada."
                )

        return cleaned_data
