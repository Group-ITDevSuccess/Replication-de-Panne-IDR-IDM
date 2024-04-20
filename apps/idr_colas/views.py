import json
import os
import re
import uuid

import pytz

from datetime import datetime, date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.db.models.functions import Cast
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F, Q, Subquery, Count, FloatField

from .form import MachineForm
from .models import MachineIdrColas, BreakdownIdrColas
from utils.script import write_log, are_valid_uuids
from ..idr_idm.form import ClientForm
from ..idr_idm.models import Jointe, Localisation, Historic, Client
from ..idr_idm.views import format_value, format_datetime


@login_required
def index(request):
    context = {
        'path': request.path,
        'form_add_machine': MachineForm(),
        'form_add_client': ClientForm()
    }
    return render(request, 'idr_colas/index.html', context)


@csrf_exempt
@login_required
def upload_file(request):
    if request.method == 'POST' and request.FILES:
        try:
            uploaded_files = request.FILES.getlist('files', None)
            id_param = request.POST.get('id', None)
            print(f"POST: {request.POST}, FILE: {request.FILES}, {uploaded_files}, {id_param}")

            if uploaded_files is not None and id_param is not None:
                breakdown = BreakdownIdrColas.objects.get(uid__exact=id_param)
                for uploaded_file in uploaded_files:
                    # Générer un UID unique pour le nom du fichier
                    uid = str(uuid.uuid4())
                    file_extension = os.path.splitext(uploaded_file.name)[1]
                    new_filename = f"{uid}{file_extension}"

                    # Enregistrer le fichier dans le répertoire media
                    filepath = os.path.join('media', new_filename)
                    with open(filepath, 'wb') as destination:
                        for chunk in uploaded_file.chunks():
                            destination.write(chunk)

                    # Créer l'objet Jointe et l'associer à Breakdown
                    fichier = Jointe.objects.create(name=uploaded_file.name, fichier=new_filename,
                                                    acteur=request.user.username)
                    breakdown.jointe.add(fichier)

                breakdown.save()

            return JsonResponse({'success': True}, status=201)
        except KeyError:
            return JsonResponse({'error': 'No image uploaded'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@csrf_exempt
def get_file_jointe(request):
    gets = json.loads(request.body.decode('utf-8'))
    uid = gets.get('uid', None)
    page = gets.get('page', 0)
    datas = []
    if uid:
        try:
            breakdown = BreakdownIdrColas.objects.get(uid__exact=uid)
            jointe = breakdown.jointe.all().values('uid', 'name', 'fichier', 'acteur', 'created_at')
            datas = [{key: format_value(value) for key, value in data.items()} for data in jointe]
        except BreakdownIdrColas.DoesNotExist:
            print("Breakdown Introuvable !")
    return JsonResponse({'data': datas, 'last_page': page}, status=200, safe=False)


@csrf_exempt
def delete_jointe(request):
    try:
        # print(f"{request.POST}, {request.body}, {request.GET}")
        # gets = json.loads(request.body.decode('utf-8'))
        uid_breakdown = request.POST.get('uid_breakdown', None)
        uid_jointe = request.POST.get('uid_jointe', None)
        if uid_breakdown and uid_jointe:
            breakdown = BreakdownIdrColas.objects.get(uid__exact=uid_breakdown)
            jointe = breakdown.jointe.get(uid__exact=uid_jointe)
            jointe.delete()
            return JsonResponse({'success': True}, status=201)
    except BreakdownIdrColas.DoesNotExist:
        print("Breakdown Introuvable !")
    except Exception as e:
        write_log(str(e))
        print("Erreur de suppression")
    return JsonResponse({'success': False}, status=301)


@csrf_exempt
@login_required
def get_all_machineidrcolas_with_breakdown_false(request):
    if request.method == 'GET':
        machines = MachineIdrColas.objects.filter(breakdown__archived=False, breakdown__isnull=False).annotate(
            localisation_name=F('breakdown__localisation__locality'),
            client_name=F('breakdown__client__name'),
            end=F('breakdown__end'),
            start=F('breakdown__start'),
            works=F('breakdown__works'),
            prevision=F('breakdown__prevision'),
            commentaire=F('breakdown__commentaire'),
            uid_name=F('breakdown__uid'),
            archived_status=F('breakdown__archived'),
            month=F('breakdown__month'),
            jde=F('breakdown__jde'),
            jointe_count=Count('breakdown__jointe')
        ).values(
            'uid_name', 'month', 'jde', 'matriculate', 'model', 'localisation_name', 'client_name', 'start',
            'prevision', 'end',
            'works', 'commentaire', 'archived_status', 'jointe_count'
        )

        breakdowns_list = [{key: format_value(value) for key, value in machine.items()} for machine in machines]
        datas = []
        for items_breakdown in breakdowns_list:
            matricule = items_breakdown.get('matriculate')
            breakdowns_archived = MachineIdrColas.objects.filter(breakdown__machineidrcolas__matriculate=matricule,
                                                                 breakdown__archived=True).annotate(
                localisation_name=F('breakdown__localisation__locality'),
                client_name=F('breakdown__client__name'),
                end=F('breakdown__end'),
                start=F('breakdown__start'),
                works=F('breakdown__works'),
                prevision=F('breakdown__prevision'),
                commentaire=F('breakdown__commentaire'),
                uid_name=F('breakdown__uid'),
                archived_status=F('breakdown__archived'),
                month=F('breakdown__month'),
                jde=F('breakdown__jde'),
                jointe_count=Count('breakdown__jointe')
            ).values(
                'uid_name', 'month', 'jde', 'matriculate', 'model', 'localisation_name', 'client_name', 'start',
                'prevision', 'end',
                'works', 'commentaire', 'archived_status', 'jointe_count'
            )
            if breakdowns_archived:
                items_breakdown['_children'] = [{key: format_value(value) for key, value in machine.items()} for machine
                                                in breakdowns_archived]

            datas.append(items_breakdown)
        return JsonResponse(datas, status=200, safe=False)
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


from django.contrib.auth.models import User  # Import the default User model if needed


@csrf_exempt
@login_required
def post_line(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            print(f"Data post_line: {data}")
            matriculate = data.get('matriculate')
            machine = MachineIdrColas.objects.get(matriculate=matriculate)

            return save_breakdown(request.user.username, machine, data, is_update=False)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Format JSON invalide.'}, status=400)
        except MachineIdrColas.DoesNotExist:
            write_log('Machine introuvable.')
            return JsonResponse({'error': "Machine non trouvée."}, status=404)
    return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)


@csrf_exempt
@login_required
def update_line(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            print(f"Data update_line: {data}")
            matriculate = data.get('matriculate')
            machine = MachineIdrColas.objects.get(matriculate=matriculate)
            return save_breakdown(request.user.username, machine, data, is_update=True)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Format JSON invalide.'}, status=400)
        except MachineIdrColas.DoesNotExist:
            write_log('Machine introuvable.')
            return JsonResponse({'error': "Machine non trouvée."}, status=404)
    return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)


def save_breakdown(acteur, machine, data, is_update=False):
    try:
        # Check if it's an update or add action
        action = 'update' if is_update else 'add'

        # Create and save Historic record
        historique = Historic(acteur=acteur, action=action, argument=json.dumps(data))
        historique.save()

        with transaction.atomic():
            if is_update:
                uid_name = 'uid_name'
                if uid_name not in data:
                    return JsonResponse({'error': 'UID du Breakdown manquant pour la mise à jour.'}, status=400)

                breakdown_uid = are_valid_uuids(data.get(uid_name))
                breakdown = BreakdownIdrColas.objects.get(uid=breakdown_uid, machineidrcolas=machine, archived=False)
            else:
                if machine.has_active_breakdown():
                    return JsonResponse({'error': 'Une machine ne peut avoir qu\'un seul Breakdown non archivé.'},
                                        status=400)

                breakdown = BreakdownIdrColas()

            # Configure Breakdown data
            for key, value in data.items():
                key = key.replace('_name', '')
                if key not in ['uid', 'client', 'matriculate', 'localisation', 'model']:
                    if key in ('start', 'end', 'prevision'):
                        value = format_datetime(value)
                    setattr(breakdown, key, value)

                elif key == 'localisation':
                    localisation = Localisation.objects.filter(locality=value).first()
                    if localisation:
                        breakdown.localisation = localisation
                    else:
                        write_log('Localisation non trouvée.')

                elif key == 'client':
                    if value is not None and value.strip():
                        client, _ = Client.objects.get_or_create(name__iexact=value)
                        breakdown.client = client
                    else:
                        breakdown.client = None

            breakdown.machineidrcolas = machine
            breakdown.save()

            # Add Historic record to Breakdown
            breakdown.historic.add(historique)
            machine.breakdown.add(breakdown)

        machine.save()
        write_log('Opération terminée !')

        if is_update:
            return JsonResponse({'message': 'Breakdown mis à jour avec succès.'}, status=200)
        else:
            return JsonResponse({'message': 'Breakdown ajouté avec succès.'}, status=201)

    except MachineIdrColas.DoesNotExist:
        write_log('Machine introuvable.')
        return JsonResponse({'error': "Machine non trouvée."}, status=404)
    except BreakdownIdrColas.DoesNotExist:
        write_log('Breakdown introuvable.')
        return JsonResponse({'error': "Breakdown non trouvé."}, status=404)
    except Exception as e:
        write_log(f'Erreur inattendue : {str(e)}')
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@login_required
def delete_breakdown(request):
    if request.method == 'POST':
        breakdown_id = request.POST.get('breakdown_id')
        try:
            breakdown = BreakdownIdrColas.objects.get(uid=breakdown_id)
            historique = Historic.objects.create(acteur=request.user.username, action='archive')
            breakdown.archived = True
            breakdown.historic.add(historique)
            breakdown.save()
            print("On a : {breakdown}".format(breakdown=breakdown))
            return JsonResponse({'success': True})
        except BreakdownIdrColas.DoesNotExist:
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
    return redirect('idr_colas:index')


@login_required
def get_all_machines_in_table(request):
    machines_assigned = BreakdownIdrColas.objects.filter(archived=False).values('machine__uid')
    machines = MachineIdrColas.objects.exclude(uid__in=Subquery(machines_assigned))

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
    data = []

    try:
        breakdowns = MachineIdrColas.objects.filter(breakdown__localisation__longitude__isnull=False,
                                                    breakdown__localisation__latitude__isnull=False,
                                                    breakdown__archived__exact=False).annotate(
            name=F('breakdown__localisation__locality'),
            lon=Cast(F('breakdown__localisation__longitude'), output_field=FloatField()),
            lat=Cast(F('breakdown__localisation__latitude'), output_field=FloatField()),

        ).values('matriculate', 'name', 'lon', 'lat')
        print(breakdowns)
        if breakdowns:
            data = [{'name': f"{breakdown['matriculate']} ({breakdown['name']})", 'lon': float(breakdown['lon']),
                     'lat': float(breakdown['lat'])} for breakdown in breakdowns]

        print(f"On a : {data}")
    except Exception as e:
        print("Une erreur a survenue !")
        write_log(str(e))
    return JsonResponse(data, safe=False)


@csrf_exempt
@login_required
def get_all_matriculate(request):
    datas = []

    machines_without_active_breakdown = MachineIdrColas.objects.annotate(
        active_breakdown_count=Count('breakdown', filter=Q(breakdown__archived=False))
    ).filter(active_breakdown_count=0)

    for machine in machines_without_active_breakdown:
        datas.append({'label': machine.matriculate, 'value': machine.matriculate})
    return JsonResponse(datas, safe=False)


@csrf_exempt
@login_required
def get_machines(request):
    machines = []

    machines_qs = MachineIdrColas.objects.all()
    for machine in machines_qs:
        machines.append({'label': machine.matriculate, 'value': machine.matriculate})
    return JsonResponse(machines, safe=False)
