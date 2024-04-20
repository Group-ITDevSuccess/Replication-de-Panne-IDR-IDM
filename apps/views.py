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
from apps.form import MachineForm, ClientForm
from apps.models import Machine, Breakdown, Localisation, Client, Jointe, Historic
from utils.script import write_log, are_valid_uuids


def extract_name(chaine):
    matches = re.match(r'(.+) \((.+)\)', chaine)
    if matches:
        locality = matches.group(1)
        commune = matches.group(2)
        return locality, commune
    else:
        return None, None


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


def format_datetime(value):
    write_log(f"======================== {value} ========================")
    if value is not None and value.strip():  # Vérifiez si la valeur n'est pas vide
        try:
            value = datetime.strptime(value, '%d/%m/%Y %H:%M:%S')
            value = timezone.make_aware(value, timezone=pytz.timezone('Indian/Antananarivo'))
            value = value.strftime('%Y-%m-%d %H:%M:%S')
            print(value)
            return value  # Format attendu par Django
        except Exception as e:
            write_log(f"Erreur pour {value} : {str(e)}")
    return None  # Retourne None si la valeur est vide ou ne peut pas être formatée


@login_required
def index(request):
    context = {
        'path': request.path,
        'form_add_machine': MachineForm(),
        'form_add_client': ClientForm()
    }
    return render(request, 'apps/index.html', context)


@csrf_exempt
@login_required
def upload_file(request):
    if request.method == 'POST' and request.FILES:
        try:
            uploaded_files = request.FILES.getlist('files', None)
            id_param = request.POST.get('id', None)
            print(f"POST: {request.POST}, FILE: {request.FILES}, {uploaded_files}, {id_param}")

            if uploaded_files is not None and id_param is not None:
                breakdown = Breakdown.objects.get(uid__exact=id_param)
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
            breakdown = Breakdown.objects.get(uid__exact=uid)
            jointe = breakdown.jointe.all().values('uid', 'name', 'fichier', 'acteur', 'created_at')
            datas = [{key: format_value(value) for key, value in data.items()} for data in jointe]
        except Breakdown.DoesNotExist:
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
            breakdown = Breakdown.objects.get(uid__exact=uid_breakdown)
            jointe = breakdown.jointe.get(uid__exact=uid_jointe)
            jointe.delete()
            return JsonResponse({'success': True}, status=201)
    except Breakdown.DoesNotExist:
        print("Breakdown Introuvable !")
    except Exception as e:
        write_log(str(e))
        print("Erreur de suppression")
    return JsonResponse({'success': False}, status=301)


@csrf_exempt
@login_required
def get_all_machine_with_breakdown_false(request):
    if request.method == 'GET':
        machines = Machine.objects.filter(breakdown__archived=False, breakdown__isnull=False).annotate(
            localisation_name=F('breakdown__localisation__locality'),
            client_name=F('breakdown__client__name'),
            appointment=F('breakdown__appointment'),
            enter=F('breakdown__enter'),
            order=F('breakdown__order'),
            start=F('breakdown__start'),
            leave=F('breakdown__leave'),
            works=F('breakdown__works'),
            prevision=F('breakdown__prevision'),
            piece=F('breakdown__piece'),
            diagnostics=F('breakdown__diagnostics'),
            achats=F('breakdown__achats'),
            imports=F('breakdown__imports'),
            decision=F('breakdown__decision'),
            uid_name=F('breakdown__uid'),
            archived_status=F('breakdown__archived'),
            jointe_count=Count('breakdown__jointe')
        ).values(
            'uid_name', 'matriculate', 'model', 'localisation_name', 'client_name', 'start',
            'appointment', 'enter', 'order', 'leave',
            'works', 'prevision', 'piece', 'diagnostics',
            'achats', 'imports', 'decision', 'archived_status', 'jointe_count'
        )

        breakdowns_list = [{key: format_value(value) for key, value in machine.items()} for machine in machines]
        datas = []
        for items_breakdown in breakdowns_list:
            matricule = items_breakdown.get('matriculate')
            breakdowns_archived = Machine.objects.filter(breakdown__machine__matriculate=matricule,
                                                         breakdown__archived=True).annotate(
                localisation_name=F('breakdown__localisation__locality'),
                client_name=F('breakdown__client__name'),
                appointment=F('breakdown__appointment'),
                enter=F('breakdown__enter'),
                order=F('breakdown__order'),
                start=F('breakdown__start'),
                leave=F('breakdown__leave'),
                works=F('breakdown__works'),
                prevision=F('breakdown__prevision'),
                piece=F('breakdown__piece'),
                diagnostics=F('breakdown__diagnostics'),
                achats=F('breakdown__achats'),
                imports=F('breakdown__imports'),
                decision=F('breakdown__decision'),
                uid_name=F('breakdown__uid'),
                archived_status=F('breakdown__archived'),
                jointe_count=Count('breakdown__jointe')
            ).values(
                'uid_name', 'matriculate', 'model', 'localisation_name', 'client_name', 'start',
                'appointment', 'enter', 'order', 'leave',
                'works', 'prevision', 'piece', 'diagnostics',
                'achats', 'imports', 'decision', 'archived_status', 'jointe_count'
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


def save_breakdown(acteur, machine, data, is_update=False):
    historique = Historic()
    try:
        # Code pour configurer historique
        historique.acteur = acteur
        action = 'update' if is_update else 'add'
        historique.action = action
        historique.argument = json.dumps(data)
        historique.save()  # Sauvegarder historique avant de l'ajouter à breakdown.historic

        with transaction.atomic():
            if is_update:
                uid_name = 'uid_name'
                if uid_name not in data:
                    return JsonResponse({'error': 'UID du Breakdown manquant pour la mise à jour.'}, status=400)

                breakdown_uid = are_valid_uuids(data.get(uid_name))
                breakdown = Breakdown.objects.get(uid=breakdown_uid, machine=machine, archived=False)
            else:
                if machine.has_active_breakdown():
                    return JsonResponse({'error': 'Une machine ne peut avoir qu\'un seul Breakdown non archivé.'},
                                        status=400)

                breakdown = Breakdown()

            for key, value in data.items():
                key = key.replace('_name', '')
                if key not in ['uid', 'client', 'matriculate', 'localisation', 'model']:
                    if key in ('start', 'leave', 'appointment', 'enter'):
                        value = format_datetime(value)
                    setattr(breakdown, key, value)

                elif key == 'localisation':
                    localisation = Localisation.objects.filter(locality=value).first()
                    if localisation:
                        breakdown.localisation = localisation
                    else:
                        write_log('Localisation non trouvée.')

                elif key == 'client':
                    if value is not None and value.strip():  # Vérifiez si la valeur n'est pas vide
                        client, _ = Client.objects.get_or_create(name__iexact=value)
                        breakdown.client = client
                    else:
                        breakdown.client = None  # Assurez-vous que le champ client est vide si la valeur est vide

            breakdown.machine = machine
            breakdown.historic.add(historique)  # Ajouter historique à breakdown.historic
            breakdown.save()  # Enregistrer breakdown

        machine.breakdown.add(breakdown)
        machine.save()

        write_log('Opération terminée !')
        if is_update:
            return JsonResponse({'message': 'Breakdown mis à jour avec succès.'}, status=200)
        else:
            return JsonResponse({'message': 'Breakdown ajouté avec succès.'}, status=201)
    except Machine.DoesNotExist:
        write_log('Machine introuvable.')
        return JsonResponse({'error': "Machine non trouvée."}, status=404)
    except Breakdown.DoesNotExist:
        write_log('Breakdown introuvable.')
        return JsonResponse({'error': "Breakdown non trouvé."}, status=404)
    except Exception as e:
        write_log(f'Erreur inattendue : {str(e)}')
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@login_required
def post_line(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            print(f"Data post_line: {data}")
            matriculate = data.get('matriculate')
            machine = Machine.objects.get(matriculate=matriculate)

            return save_breakdown(request.user.username, machine, data, is_update=False)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Format JSON invalide.'}, status=400)
        except Machine.DoesNotExist:
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
            machine = Machine.objects.get(matriculate=matriculate)
            return save_breakdown(request.user.username, machine, data, is_update=True)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Format JSON invalide.'}, status=400)
        except Machine.DoesNotExist:
            write_log('Machine introuvable.')
            return JsonResponse({'error': "Machine non trouvée."}, status=404)
    return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)


@csrf_exempt
@login_required
def delete_breakdown(request):
    if request.method == 'POST':
        breakdown_id = request.POST.get('breakdown_id')
        try:
            breakdown = Breakdown.objects.get(uid=breakdown_id)
            historique = Historic.objects.create(acteur=request.user.username, action='archive')
            breakdown.archived = True
            breakdown.historic.add(historique)
            breakdown.save()
            print("On a : {breakdown}".format(breakdown=breakdown))
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
def get_all_machines_in_table(request):
    machines_assigned = Breakdown.objects.filter(archived=False).values('machine__uid')
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
    data = []

    try:
        breakdowns = Machine.objects.filter(breakdown__localisation__longitude__isnull=False,
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

    machines_without_active_breakdown = Machine.objects.annotate(
        active_breakdown_count=Count('breakdown', filter=Q(breakdown__archived=False))
    ).filter(active_breakdown_count=0)

    for machine in machines_without_active_breakdown:
        datas.append({'label': machine.matriculate, 'value': machine.matriculate})
    return JsonResponse(datas, safe=False)


@csrf_exempt
@login_required
def get_all_client(request):
    datas = []

    clients = Client.objects.all().order_by('name')

    for machine in clients:
        datas.append({'label': machine.name, 'value': machine.name})
    return JsonResponse(datas, safe=False)


@csrf_exempt
@login_required
def get_machines(request):
    machines = []

    machines_qs = Machine.objects.all()
    for machine in machines_qs:
        machines.append({'label': machine.matriculate, 'value': machine.matriculate})
    return JsonResponse(machines, safe=False)


@csrf_exempt
def add_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Client ajouté avec succès.")
            except IntegrityError:
                messages.error(request, "Un client avec ce nom existe déjà.")
        else:
            # Vérification spécifique pour le nom du client
            if 'name' in form.errors:
                messages.warning(request, "Un client avec ce nom existe déjà.")
            else:
                messages.error(request, "Formulaire invalide. Veuillez corriger les erreurs.")
    else:
        messages.warning(request, "Méthode non autorisée !")
    return redirect('apps:index')


@csrf_exempt
def delete_client(request, uid):
    try:
        client = Client.objects.get(uid__exact=uid)
        client.delete()
    except Client.DoesNotExist:
        messages.warning(request, "Client Introuvable ")
    return redirect('apps:index')
