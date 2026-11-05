
from django import forms

from .models import Chofer


class ChoferForm(forms.ModelForm):

    class Meta:
        model = Chofer

        fields = [
            "nombre",
            "apellido",
            "dni",
            "activo",
        ]

        labels = {
            "nombre": "Nombre",
            "apellido": "Apellido",
            "dni": "DNI",
            "activo": "Chofer activo",
        }

        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "apellido": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "dni": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "activo": forms.CheckboxInput(
                attrs={"class": "form-check-input"}
            ),
        }
