import uuid

from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F
from django.views.decorators.csrf import csrf_exempt

from utils.script import ldap_login_connection, write_log, are_valid_uuids
from .forms import LoginForm, ProfileForm
from .models import CustomUser, CustomPermission

# Create your views here.
from django.contrib.auth.decorators import user_passes_test


@login_required
def index(request):
    print(request.user)
    context = {
        'path': request.path
    }
    return render(request, 'guard/index.html', context)


@login_required
@csrf_exempt
def all_users_json(request):
    users = CustomUser.objects.all().annotate(id=F('uid')).values(
        'id', 'username', 'first_name', 'last_name', 'level_1', 'level_2', 'level_3', 'level_4', 'autoriser',
        'is_active',
        'is_staff', 'is_superuser',
    )
    data = list(users)
    return JsonResponse(data, safe=False)


@csrf_exempt
@login_required
def get_all_permission(request):
    data = []
    permissions = CustomPermission.objects.all()
    for permission in permissions:
        data.append({
            'index': permission.uid,
            'name': permission.name
        })
    return JsonResponse(data, safe=False)


@login_required
@csrf_exempt
def update_user_json(request):
    uid = are_valid_uuids(request.POST.get('id', None))
    message = "Uid est Null !"
    if uid is not None:
        try:
            user = CustomUser.objects.get(uid__exact=uid)
            value = request.POST.get('value')
            if value == 'true':
                value = True
            elif value == 'false':
                value = False
            setattr(user, request.POST.get('key'), value)
            user.save()
            return JsonResponse({'success': 'User Modifier'}, status=201)

        except CustomUser.DoesNotExist:
            message = "Utilisateur n'existe pas!"
        except Exception as e:
            write_log(str(e))
    return JsonResponse({'error': message}, status=404)


@login_required
@csrf_exempt
def create_user_json(request):
    uid = uuid.uuid4()
    try:
        user, created = CustomUser.objects.get_or_create(uid__exact=uid)
        if created:
            data = {
                "id": user.uid,
            }
            return JsonResponse({"success": True, "message": "Created new User", "data": data}, safe=False, status=201)
    except Exception as e:
        write_log(str(e))

    return JsonResponse({"success": False, "message": "User already exists"}, safe=False)


@login_required
@csrf_exempt
def delete_user_json(request):
    uids = are_valid_uuids(request.POST.getlist('id', None))
    if uids is not None:
        user = CustomUser.objects.get(uid__in=uids)
        user.delete()
        return JsonResponse({"success": True, "message": "User Deleted", }, safe=False, status=201)
    return JsonResponse({"success": False, "message": "User already exists"}, safe=False)


def is_user_not_authenticated(user):
    return not user.is_authenticated


class LoginLDAP(View):
    def get(self, request):
        forms = LoginForm()  # Instantiate the form
        context = {'form': forms}
        return render(request, 'guard/login.html', context)

    def post(self, request):
        forms = LoginForm(request.POST)
        if forms.is_valid():
            username = forms.cleaned_data['username']
            password = forms.cleaned_data['password']

            # Check if username is allowed for LDAP authentication
            if username not in ['admin.dev', 'user.dev', 'user.staff']:
                connexion = ldap_login_connection(username=username, password=password)
                if connexion:
                    try:
                        user_get = CustomUser.objects.get(username=username)
                        if user_get.autoriser:
                            login(request, user_get)
                            return redirect('idr_idm:index')
                        else:
                            messages.error(request, "Vous n'êtes pas encore autorisé à vous connecter.")
                    except CustomUser.DoesNotExist:
                        # Create user if not found in database
                        email = connexion.get('email', '')
                        lastname = connexion.get('lastname', '')
                        firstname = connexion.get('firstname', '')

                        user_get = CustomUser(
                            username=username,
                            last_name=lastname,
                            first_name=firstname,
                            email=email,
                            autoriser=False,
                            is_staff=False,
                            is_superuser=False
                        )
                        user_get.save()
                        messages.success(request, "Votre compte a été créé.")
                else:
                    messages.error(request, "Login ou Mot de passe Incorrect !")
            else:
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('idr_idm:index')
                else:
                    messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
        else:
            messages.error(request, "Le formulaire de connexion est invalide !")
        return redirect('guard:login')


@login_required
def logout_ldap(request):
    msg = f"Au-revoir {request.user.last_name} {request.user.first_name} !"
    all_message = messages.get_messages(request)
    if all_message:
        for message in all_message:
            if message.tags == 'success':
                message.used = True

    logout(request)
    messages.success(request, msg)
    return redirect('guard:login')


# Create your views here.
@login_required
def profile(request):
    user = get_object_or_404(CustomUser, username=request.user)
    # write_log(f"User : {user}", level=logging.INFO)
    if request.method == 'POST':
        forms = ProfileForm(request.POST, instance=user)
        # write_log(f"Forms : {forms}", level=logging.INFO)
        if forms.is_valid():
            forms.save()
            messages.success(request, 'Sauvegarder avec Success!')
            return redirect('guard:profile')
    else:
        user, create = CustomUser.objects.get_or_create(username=request.user)
        forms = ProfileForm(instance=user)

    context = {
        'form': forms,
        'path': request.path
    }
    return render(request, 'guard/profile.html', context)
