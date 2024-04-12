import json
from django.utils.translation import gettext as _

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F  # Importer F depuis django.db.models

from apps.form import MachineForm, SearchForm
from apps.models import Machine, Company, Breakdown


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
        'get_machines_url': '',
        'get_breakdown_url': ''
    }

    if companies:
        companies_str = ','.join(str(company) for company in companies)
        context['companies'] = companies_str
        context['get_machines_url'] = reverse('apps:get_machines', kwargs={'company': companies_str})
        context['get_breakdown_url'] = reverse('apps:get_breakdown', kwargs={'company': companies_str})

    return render(request, 'apps/index.html', context)


@csrf_exempt
def get_breakdown(request, company):
    if request.method == 'GET':
        breakdowns_list = []
        company_names = company.split(',')
        if len(company_names) > 0:
            breakdowns = Breakdown.objects.filter(company__name__in=company_names).annotate(
                company_name=F('company__name'),
                matriculate=F('machine__matriculate'),
                model=F('machine__model'),
                location_name=F('location__name'),
                client_name=F('client__name')
            ).values(
                'uid', 'company_name', 'matriculate', 'model', 'location_name', 'client_name', 'start', 'end',
                'appointment', 'enter', 'exit', 'order'
            )

            breakdowns_list = list(breakdowns)
            print(f"BREAKDOWN: {breakdowns_list}")
        return JsonResponse(breakdowns_list, status=200, safe=False)
    else:
        return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)


@csrf_exempt
def delete_breakdown(request):
    if request.method == 'POST':
        breakdown_id = request.POST.get('breakdown_id')
        try:
            breakdown = Breakdown.objects.get(uid=breakdown_id)
            breakdown.delete()
            return JsonResponse({'success': True})
        except Breakdown.DoesNotExist:
            return JsonResponse({'error': 'Breakdown not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def create_machine(request):
    if request.method == 'POST':
        form = MachineForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            messages.warning(request, "Formulaire Invalide !")
    return redirect('apps:index')


def get_all_companies(request):
    companies = Company.objects.all()
    datas = []
    for companie in companies:
        datas.append({'label': companie.name, 'value': companie.name})
    return JsonResponse(datas, safe=False)


def get_all_machines_in_table(request):
    machines = Machine.objects.all()

    machines_data = []

    for machine in machines:
        machine_data = {
            'matriculate': machine.matriculate,
            'model': machine.model,
            'description': machine.description,
        }
        machines_data.append(machine_data)

    return JsonResponse({'data': machines_data}, safe=False)


@csrf_exempt
def get_all_matriculate(request):
    datas = []
    machines_qs = Machine.objects.all()
    for machine in machines_qs:
        datas.append({'label': machine.matriculate, 'value': machine.matriculate})
    return JsonResponse(datas, safe=False)


@csrf_exempt
def get_machines(request, company=None):
    machines = []

    machines_qs = Machine.objects.all()
    for machine in machines_qs:
        machines.append({'label': machine.matriculate, 'value': machine.matriculate})
    return JsonResponse(machines, safe=False)


@csrf_exempt
def post_line(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        matriculate = data.get('matriculate')
        company_name = data.get('company_name')

        try:
            machine = Machine.objects.get(matriculate=matriculate)
            company = Company.objects.get(name=company_name)
            if Breakdown.objects.filter(machine=machine).exists():
                return JsonResponse({'error': "L'immatriculation sélectionnée est déjà utilisée."},
                                    status=409)  # 409: Conflict
            Breakdown.objects.update_or_create(company=company, machine=machine)
            return JsonResponse({'message': 'Données enregistrées avec succès.'}, status=201)  # 201: Created
        except Machine.DoesNotExist:
            return JsonResponse({'error': "Machine non trouvée."}, status=404)  # 404: Not Found
        except Company.DoesNotExist:
            return JsonResponse({'error': "Société non trouvée."}, status=404)
        except Exception as e:
            print('error', str(e))
            return JsonResponse({'error': str(e)}, status=500)  # 500: Internal Server Error

    return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)  # 405: Method Not Allowed
