import json
import os.path
import re
from datetime import datetime, date

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.context_processors import media
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F

from apps.form import MachineForm, SearchForm
from apps.models import Machine, Company, Breakdown, Localisation


def extract_name(chaine):
    matches = re.match(r'(.+) \((.+)\)', chaine)
    if matches:
        locality = matches.group(1)
        commune = matches.group(2)
        return locality, commune
    else:
        return None, None


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
        'get_breakdown_url': ''
    }

    if companies:
        companies_str = ','.join(str(company) for company in companies)
        context['companies'] = companies_str
        context['get_breakdown_url'] = reverse('apps:get_breakdown', kwargs={'company': companies_str})

    return render(request, 'apps/index.html', context)


@csrf_exempt
def get_breakdown(request, company):
    if request.method == 'GET':
        breakdowns_list = []
        company_names = company.split(',')
        if len(company_names) > 0:
            breakdowns = Breakdown.objects.filter(company__name__in=company_names).annotate(
                company_name=F('company__name'),  # Renommer la clé 'company_name' en 'societe'
                matriculate=F('machine__matriculate'),  # Renommer la clé 'matriculate' en 'immatriculation'
                model=F('machine__model'),  # Renommer la clé 'model' en 'modele'
                localisation_name=F('localisation__locality'),
                # Renommer la clé 'localisation_name' en 'nom_emplacement'
                client_name=F('client__name')  # Renommer la clé 'client_name' en 'nom_client'
            ).values(
                'uid', 'company_name', 'matriculate', 'model', 'localisation_name', 'client_name', 'start', 'end',
                'appointment', 'enter', 'exit', 'order', 'leave', 'works'
            )

            breakdowns_list = list(breakdowns)
            for breakdown in breakdowns_list:
                for key, value in breakdown.items():
                    if isinstance(value, datetime):
                        breakdown[key] = value.strftime('%d/%m/%Y')
                    elif isinstance(value, date):
                        breakdown[key] = value.strftime('%d/%m/%Y')
        return JsonResponse(breakdowns_list, status=200, safe=False)
    else:
        return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)


@csrf_exempt
def gat_all_localisation(request):
    data = []
    localisations = Localisation.objects.all().order_by('locality')
    for localisation in localisations:
        data.append({'label': localisation.locality, 'value': f"{localisation.locality} ({localisation.commune}) "})
    return JsonResponse(data, status=200, safe=False)


def process_data(data, is_update=False):
    matriculate = data.get('matriculate')
    company_name = data.get('company_name')
    try:
        machine = Machine.objects.get(matriculate=matriculate)
        model = data.get('model')
        if model != '' and model:
            machine.model = model
            machine.save()
        company = Company.objects.get(name=company_name)
        if is_update:
            breakdown = Breakdown.objects.get(uid__exact=data.get('uid'))
        else:
            breakdown, _ = Breakdown.objects.get_or_create(company=company, machine=machine)
        print(data)
        for key, value in data.items():
            key = (str(key).replace('_name', ''))

            if key not in ['uid', 'company', 'client', 'matriculate', 'model']:
                if key in ['start', 'end', 'enter', 'appointment', 'exit', 'leave'] and value is not None:
                    try:
                        value = datetime.strptime(value, '%d/%m/%Y')
                    except ValueError:
                        pass
                if key == 'localisation':
                    locality, commune = extract_name(value)
                    localisation = Localisation.objects.filter(locality=locality, commune=commune).first()
                    if localisation:
                        breakdown.localisation = localisation
                    else:
                        # Gérer le cas où la localisation n'est pas trouvée
                        return JsonResponse({'error': 'Localisation non trouvée.'}, status=404)
                else:
                    setattr(breakdown, key, value)
        breakdown.save()
        return JsonResponse({'message': 'Données enregistrées avec succès.'}, status=201)  # 201: Created
    except Machine.DoesNotExist:
        return JsonResponse({'error': "Machine non trouvée."}, status=404)  # 404: Not Found
    except Company.DoesNotExist:
        return JsonResponse({'error': "Société non trouvée."}, status=404)
    except Breakdown.DoesNotExist:
        return JsonResponse({'error': "Breakdown non trouvé."}, status=404)
    except Exception as e:
        print('error', str(e))
        return JsonResponse({'error': str(e)}, status=500)  # 500: Internal Server Error


@csrf_exempt
def update_line(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        return process_data(data, is_update=True)
    return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)  # 405: Method Not Allowed


@csrf_exempt
def post_line(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        return process_data(data)
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
def get_all_breakdown(request):
    breakdowns = Breakdown.objects.exclude(localisation__isnull=True)
    company_data = {}  # Dictionnaire pour stocker les données par entreprise

    for value in breakdowns:
        data = {
            'name': f"{value.machine.matriculate}",
            'lat': float(value.localisation.longitude),
            'lon': float(value.localisation.latitude)
        }
        if value.company.name not in company_data:
            company_data[value.company.name] = {
                'data': [data]
            }
        else:
            company_data[value.company.name]['data'].append(data)

    series = [
        {
            'type': 'tiledwebmap',
            'name': 'Map Societe',
            'provider': {
                'type': 'OpenStreetMap'
            },
            'showInLegend': False
        }
    ]
    company_colors = {
        "ID Motors": 'url(https://www.highcharts.com/samples/graphics/museum.svg)',  # Red
        "ID Rental": 'url(https://www.highcharts.com/samples/graphics/building.svg)',  # Blue
    }
    # Ajouter les données par entreprise au dictionnaire 'series'
    for company_name, company_info in company_data.items():
        company_series = {
            'type': 'mappoint',
            'name': company_name,
            'marker': {
                'symbol': company_colors.get(company_name, "#cccccc"),  # Use company-specific SVG
                'width': 24,
                'height': 24,
            },
            'data': company_info['data']
        }
        series.append(company_series)
    print(series)
    return JsonResponse(series, safe=False)


@csrf_exempt
def get_all_matriculate(request):
    datas = []
    machines_qs = Machine.objects.all()
    for machine in machines_qs:
        datas.append({'label': machine.matriculate, 'value': machine.matriculate})
    return JsonResponse(datas, safe=False)


@csrf_exempt
def get_machines(request):
    machines = []

    machines_qs = Machine.objects.all()
    for machine in machines_qs:
        machines.append({'label': machine.matriculate, 'value': machine.matriculate})
    return JsonResponse(machines, safe=False)
