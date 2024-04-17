import json
import logging
import os.path
import re
from datetime import datetime, date

import pytz
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.context_processors import media
from django.urls import reverse
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F, Subquery

from apps.form import MachineForm, SearchForm
from apps.models import Machine, Company, Breakdown, Localisation

logger = logging.getLogger(__name__)


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

    return render(request, 'apps/index.html', context)


@csrf_exempt
def get_breakdown(request):
    if request.method == 'GET':
        breakdowns = Breakdown.objects.all().annotate(
            matriculate=F('machine__matriculate'),  # Renommer la clé 'matriculate' en 'immatriculation'
            model=F('machine__model'),  # Renommer la clé 'model' en 'modele'
            localisation_name=F('localisation__locality'),
            client_name=F('client__name')  # Renommer la clé 'client_name' en 'nom_client'
        ).values(
            'uid', 'matriculate', 'model', 'localisation_name', 'client_name', 'start',
            'appointment', 'enter', 'order', 'leave', 'works', 'prevision', 'piece', 'diagnostics', 'achats', 'imports',
            'decision'
        )

        def format_value(value):
            if isinstance(value, datetime):
                return value.strftime('%d/%m/%Y %H:%M:%S')  # Format français date et heure
            elif isinstance(value, date):
                return value.strftime('%d/%m/%Y')  # Format français date
            return value

        breakdowns_list = [{key: format_value(value) for key, value in breakdown.items()} for breakdown in breakdowns]
        return JsonResponse(breakdowns_list, status=200, safe=False)
    else:
        return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)


@csrf_exempt
def gat_all_localisation(request):
    data = []
    localisations = Localisation.objects.all().order_by('locality')
    for localisation in localisations:
        data.append({'label': localisation.locality, 'value': localisation.locality})
    return JsonResponse(data, status=200, safe=False)


def process_data(data, is_update=False):
    matriculate = data.get('matriculate')
    try:
        machine = Machine.objects.get(matriculate=matriculate)
        model = data.get('model')
        if model:
            machine.model = model
            machine.save()

        if is_update:
            breakdown = Breakdown.objects.get(uid=data.get('uid'))
        else:
            breakdown, _ = Breakdown.objects.get_or_create(machine=machine)

        for key, value in data.items():
            key = str(key).replace('_name', '')
            if key not in ['uid', 'client', 'matriculate', 'model']:
                if key in ['start', 'end', 'enter', 'appointment', 'leave'] and value is not None:
                    try:
                        # value = pytz.timezone('UTC').localize(value)

                        print(f"Debut : {value}")
                        # value = value.strftime(%Y-%m-%d %H:%M:%S)
                        value = datetime.strptime(value, '%d/%m/%Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                        print(f"Fin : {value}")
                        # setattr(breakdown, key, value)
                    except ValueError:
                        print(f"Erreur de conversion de date : {value}")
                        pass

                if key == 'localisation':
                    localisation = Localisation.objects.filter(locality=value).first()
                    if localisation:
                        breakdown.localisation = localisation
                    else:
                        logger.error('Localisation non trouvée.')
                        # return JsonResponse({'error': 'Localisation non trouvée.'}, status=404)
                else:
                    setattr(breakdown, key, value)

        breakdown.save()
        logger.info('Enregistrement terminé !')
        return JsonResponse({'message': 'Données enregistrées avec succès.'}, status=201)
    except Machine.DoesNotExist:
        logger.error('Machine introuvable.')
        return JsonResponse({'error': "Machine non trouvée."}, status=404)
    except Breakdown.DoesNotExist:
        logger.error('Breakdown introuvable.')
        return JsonResponse({'error': "Breakdown non trouvé."}, status=404)
    except Exception as e:
        logger.exception('Erreur inattendue.')
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def update_line(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            return process_data(data, is_update=True)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Format JSON invalide.'}, status=400)
    return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)


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
    machines_assigned = Breakdown.objects.values('machine__uid')
    machines = Machine.objects.exclude(uid__in=Subquery(machines_assigned))

    machines_data = []

    for machine in machines:
        machine_data = {
            'uid': str(machine.uid),
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
    series = []
    # for value in breakdowns:
    #     data = {
    #         'name': f"{value.machine.matriculate}",
    #         'lat': float(value.localisation.longitude),
    #         'lon': float(value.localisation.latitude)
    #     }
    #     if value.company.name not in company_data:
    #         company_data[value.company.name] = {
    #             'data': [data]
    #         }
    #     else:
    #         company_data[value.company.name]['data'].append(data)
    #
    # series = [
    #     {
    #         'type': 'tiledwebmap',
    #         'name': 'Map Societe',
    #         'provider': {
    #             'type': 'OpenStreetMap'
    #         },
    #         'showInLegend': False
    #     }
    # ]
    # company_colors = {
    #     "ID Motors": 'url(https://www.highcharts.com/samples/graphics/museum.svg)',  # Red
    #     "ID Rental": 'url(https://www.highcharts.com/samples/graphics/building.svg)',  # Blue
    # }
    # # Ajouter les données par entreprise au dictionnaire 'series'
    # for company_name, company_info in company_data.items():
    #     company_series = {
    #         'type': 'mappoint',
    #         'name': company_name,
    #         'marker': {
    #             'symbol': company_colors.get(company_name, "#cccccc"),  # Use company-specific SVG
    #             'width': 24,
    #             'height': 24,
    #         },
    #         'data': company_info['data']
    #     }
    #     series.append(company_series)
    return JsonResponse(series, safe=False)


@csrf_exempt
def get_all_matriculate(request):
    datas = []
    machines_assigned = Breakdown.objects.values('machine__uid')

    # Query to retrieve machines that are not yet assigned to breakdowns
    machines = Machine.objects.exclude(uid__in=Subquery(machines_assigned))
    for machine in machines:
        datas.append({'label': machine.matriculate, 'value': machine.matriculate})
    return JsonResponse(datas, safe=False)


@csrf_exempt
def get_machines(request):
    machines = []

    machines_qs = Machine.objects.all()
    for machine in machines_qs:
        machines.append({'label': machine.matriculate, 'value': machine.matriculate})
    return JsonResponse(machines, safe=False)
