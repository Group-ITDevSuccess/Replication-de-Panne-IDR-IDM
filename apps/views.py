from django.shortcuts import render

from apps.form import SearchForm, MachineForm


# Create your views here.
def index(request):
    context = {
        'form': SearchForm(),
        'form_add_machine': MachineForm()
    }
    return render(request, 'apps/index.html', context)
