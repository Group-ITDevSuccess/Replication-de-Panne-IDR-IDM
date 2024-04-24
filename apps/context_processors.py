from apps.idr_idm.models import Client


def context_processor_navbar(request):
    used_clients = Client.objects.filter(used=True).values('uid', 'name')
    return {'navs': used_clients}
