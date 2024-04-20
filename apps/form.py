from django import forms
from django_select2.forms import ModelSelect2Widget

from apps.models import Machine, Client


class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = ['matriculate', 'model']
        labels = {
            'matriculate': 'Matricule',
            'model': 'Model',
        }
        widgets = {
            'matriculate': forms.TextInput(attrs={'class': 'form-control', 'required': True,
                                                  'placeholder': 'Immat ou N° Serie'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'required': False,
                                            'placeholder': 'Modèle / Remorque'}),

        }


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'email', 'phone', 'localisation']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du client'}),
            'email': forms.EmailInput(
                attrs={'class': 'form-control', 'placeholder': 'Email du client', 'required': False, }),
            'phone': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Téléphone du client', 'required': False, }),
            'localisation': forms.Select(
                attrs={'class': 'selectpicker', 'data-width': '150px', 'data-style': "btn-danger", 'required': False,
                       'data-header': 'Localisation du client'}),
        }
