import json
import re
import pytz

from datetime import datetime, date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F, Subquery

from apps.form import MachineForm, SearchForm
from apps.models import Machine, Company, Breakdown, Localisation, Client
from utils.script import write_log


def extract_name(chaine):
    matches = re.match(r'(.+) \((.+)\)', chaine)
    if matches:
        locality = matches.group(1)
        commune = matches.group(2)
        return locality, commune
    else:
        return None, None


@login_required
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
        'path': request.path,
        'form_add_machine': MachineForm(),
        'get_breakdown_url': ''
    }

    if companies:
        companies_str = ','.join(str(company) for company in companies)
        context['companies'] = companies_str

    return render(request, 'apps/index.html', context)


@csrf_exempt
@login_required
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
        print(breakdowns)

        def format_value(value):
            if isinstance(value, datetime):
                if timezone.is_aware(value):  # Vérifie si l'objet datetime est déjà conscient du fuseau horaire
                    value = timezone.make_naive(value)  # Convertit l'objet datetime en objet datetime naïf
                value = timezone.make_aware(value, timezone=pytz.timezone('Indian/Antananarivo'))
                return value.strftime('%d/%m/%Y %H:%M:%S')  # Format français date et heure
            elif isinstance(value, date):
                if timezone.is_aware(value):  # Vérifie si l'objet date est déjà conscient du fuseau horaire
                    value = timezone.make_naive(value)  # Convertit l'objet date en objet date naïf
                value = timezone.make_aware(value, timezone=pytz.timezone('Indian/Antananarivo'))
                return value.strftime('%d/%m/%Y')  # Format français date
            return value

        breakdowns_list = [{key: format_value(value) for key, value in breakdown.items()} for breakdown in breakdowns]
        return JsonResponse(breakdowns_list, status=200, safe=False)
    else:
        return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)


@csrf_exempt
@login_required
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
                        value = datetime.strptime(value, '%d/%m/%Y %H:%M:%S')

                        setattr(breakdown, key, value)
                    except ValueError:
                        print(f"Erreur de conversion de date : {value}")
                        pass

                if key == 'localisation':
                    localisation = Localisation.objects.filter(locality=value).first()
                    if localisation:
                        breakdown.localisation = localisation
                    else:
                        write_log('Localisation non trouvée.')
                else:
                    setattr(breakdown, key, value)

                if key == 'client':
                    print(value)
                    client, _ = Client.objects.get_or_create(name__iexact=value)
                    breakdown.client = client
        breakdown.save()
        write_log('Enregistrement terminé !')
        return JsonResponse({'message': 'Données enregistrées avec succès.'}, status=201)
    except Machine.DoesNotExist:
        write_log('Machine introuvable.')
        return JsonResponse({'error': "Machine non trouvée."}, status=404)
    except Breakdown.DoesNotExist:
        write_log('Breakdown introuvable.')
        return JsonResponse({'error': "Breakdown non trouvé."}, status=404)
    except Exception as e:
        write_log('Erreur inattendue.')
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@login_required
def update_line(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            return process_data(data, is_update=True)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Format JSON invalide.'}, status=400)
    return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)


@csrf_exempt
@login_required
def update_line(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        return process_data(data, is_update=True)
    return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)  # 405: Method Not Allowed


@csrf_exempt
@login_required
def post_line(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        return process_data(data)
    return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)


@csrf_exempt
@login_required
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


@login_required
def create_machine(request):
    if request.method == 'POST':
        form = MachineForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            messages.warning(request, "Formulaire Invalide !")
    return redirect('apps:index')


@login_required
def get_all_companies(request):
    companies = Company.objects.all()
    datas = []
    for companie in companies:
        datas.append({'label': companie.name, 'value': companie.name})
    return JsonResponse(datas, safe=False)


@login_required
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
@login_required
def get_all_breakdown(request):
    breakdowns = Breakdown.objects.exclude(localisation__isnull=True)
    data = []
    for value in breakdowns:
        data.append({
            'name': f"{value.machine.matriculate}",
            'lat': float(value.localisation.longitude),
            'lon': float(value.localisation.latitude)
        })
    print(f"On a : {data}")
    return JsonResponse(data, safe=False)


@csrf_exempt
@login_required
def get_all_matriculate(request):
    datas = []
    machines_assigned = Breakdown.objects.values('machine__uid')

    # Query to retrieve machines that are not yet assigned to breakdowns
    machines = Machine.objects.exclude(uid__in=Subquery(machines_assigned))
    for machine in machines:
        datas.append({'label': machine.matriculate, 'value': machine.matriculate})
    return JsonResponse(datas, safe=False)


@csrf_exempt
@login_required
def get_machines(request):
    machines = []

    machines_qs = Machine.objects.all()
    for machine in machines_qs:
        machines.append({'label': machine.matriculate, 'value': machine.matriculate})
    return JsonResponse(machines, safe=False)
