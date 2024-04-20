from django import forms
from django_select2.forms import ModelSelect2Widget

from apps.models import Machine


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
            'model': forms.TextInput(attrs={'class': 'form-control', 'required': True,
                                            'placeholder': 'Modèle / Remorque'}),

        }
