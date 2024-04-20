from django import forms

from .models import MachineIdrColas


class MachineForm(forms.ModelForm):
    class Meta:
        model = MachineIdrColas
        fields = ['matriculate', 'model']
        labels = {
            'matriculate': 'Matricule',
            'model': 'Model',
        }
        widgets = {
            'matriculate': forms.TextInput(attrs={'class': 'form-control', 'required': 'false',
                                                  'placeholder': 'Immat ou N° Serie'}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'required': 'false',
                                            'placeholder': 'Modèle / Remorque'}),

        }

