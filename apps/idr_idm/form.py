from django import forms


from .models import MachineIdrIdm, Client


class MachineForm(forms.ModelForm):
    class Meta:
        model = MachineIdrIdm
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
                attrs={'class': 'selectpicker show-tick', 'data-size': 10, 'data-live-search': 'true',
                       'data-width': '145px', 'data-style': "btn-danger", 'required': False,
                       'data-header': 'Localisation du client'}),
        }
