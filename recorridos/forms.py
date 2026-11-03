from django import forms
from .models import Autobus


class AutobusForm(forms.ModelForm):
    class Meta:
        model = Autobus
        fields = [
            "patente",
            "numero_unidad",
            "fecha_compra",
            "estado",
        ]

        widgets = {
            "patente": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "numero_unidad": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "fecha_compra": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "estado": forms.Select(
                attrs={"class": "form-select"}
            ),
        }