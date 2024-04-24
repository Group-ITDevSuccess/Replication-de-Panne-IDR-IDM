from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from apps.idr_idm.form import MachineForm
from apps.idr_idm.models import Client
from utils.script import write_log


# Create your views here.
def index(request, uid):
    # client = Client.objects.get(uid=uid, used__exact=True)
    client = get_object_or_404(Client, uid=uid, used__exact=True)
    context = {
        'form_add_machine': MachineForm(),
        'uid_client': client.uid,
        'name_client': client.name,
    }
    return render(request, 'detail/index.html', context)
