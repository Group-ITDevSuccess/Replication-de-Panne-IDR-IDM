from django import forms
from django_select2.forms import ModelSelect2Widget

from apps.models import Machine, Company, Breakdown


class SearchForm(forms.Form):
    company = forms.ModelMultipleChoiceField(
        queryset=Company.objects.all().order_by('name'),
        label='Société',
        widget=forms.SelectMultiple(
            attrs={'class': 'selectpicker mr-2', 'data-style': "btn-primary", 'multiple': True,
                   "data-live-search": "true",
                   "data-header": "Choisir un Societe...", "title": "List des Sociétés", "data-size": "8"}),
        required=True
    )


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
        }


class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = ['matriculate', 'model', 'description']
        labels = {
            'matriculate': 'Matricule',
            'model': 'Model',
            'description': 'Description',
        }
        widgets = {
            'matriculate': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'model': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Ici les informations supplémentaires',
                       'required': False}),
        }


class BreakdownForm(forms.ModelForm):
    class Meta:
        model = Breakdown
        fields = '__all__'  # Include all fields
        widgets = {
            'company': ModelSelect2Widget(model=Company, search_fields=['name__icontains']),
            'machine': ModelSelect2Widget(model=Machine, search_fields=['matriculate__icontains']),
            # Other fields as needed
        }
