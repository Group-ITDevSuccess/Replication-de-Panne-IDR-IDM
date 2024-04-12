from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from slugify import slugify

from apps.form import SearchForm, MachineForm
from apps.models import Machine, Company


# Create your views here.

# @login_required
def index(request):
    companies = []

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            companies = form.cleaned_data['company']
        else:
            print("Formulaire Invalide !")
    else:
        form = SearchForm()
    context = {
        'form': form,
        'form_add_machine': MachineForm(),
        'get_machines_url': ''
    }
    if companies:
        companies = str(','.join(str(company) for company in companies))
        context['companies'] = companies
        context['get_machines_url'] = reverse('apps:get_machines', kwargs={'company': context['companies']})

    return render(request, 'apps/index.html', context)


def create_machine(request):
    if request.method == 'POST':
        form = MachineForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            messages.warning(request, "Formulaire Invalide !")
    return redirect('apps:index')


def get_all_machines(request):
    machines = Machine.objects.all()

    # Créez une liste pour stocker les données JSON des machines
    machines_data = []

    # Parcourez toutes les machines et créez un dictionnaire pour chaque machine
    for machine in machines:
        machine_data = {
            'matriculate': machine.matriculate,
            'model': machine.model,
            'description': machine.description,
            'company': machine.company.name,  # Assurez-vous que le modèle Company a un champ 'name'
        }
        machines_data.append(machine_data)

    # Retournez les données JSON en utilisant JsonResponse
    return JsonResponse({'data': machines_data})


@csrf_exempt
def get_machines(request, company=None):
    machines = []
    company = company.split(',')

    if company is not None and len(company) > 0:
        companies = Company.objects.filter(name__in=company)
        if companies:
            machines_qs = Machine.objects.filter(company__in=companies)
            for machine in machines_qs:
                machines.append({'label': machine.matriculate, 'value': machine.matriculate})
    return JsonResponse(machines, safe=False)
