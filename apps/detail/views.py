from django.contrib import messages
from django.shortcuts import render, redirect

from apps.idr_idm.form import MachineForm
from apps.idr_idm.models import Client
from utils.script import write_log


# Create your views here.
def index(request, uid):
    try:
        client = Client.objects.get(uid=uid)
        context = {
            'form_add_machine': MachineForm(),
            'uid_client': client.uid,
            'name_client': client.name,
        }
        return render(request, 'detail/index.html', context)
    except Exception as e:
        write_log(str(e))
        messages.error(request, "Client Introuvable !")
        return redirect('idr_idm:index')
