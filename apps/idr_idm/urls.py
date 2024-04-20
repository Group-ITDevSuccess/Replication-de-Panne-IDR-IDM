from django.urls import path
from . import views

app_name = 'idr_idm'
urlpatterns = [
    path('', views.index, name='index'),
    path('idr-idm/post-line-data/', views.post_line, name='post_line'),
    path('idr-idm/update-line-data/', views.update_line, name='update_line'),
    path('idr-idm/create-machine/', views.create_machine, name='create_machine'),
    path('idr-idm/get-all-machines-in-table/', views.get_all_machines_in_table, name='get_all_machines_in_table'),
    path('idr-idm/get-all-matriculate/', views.get_all_matriculate, name='get_all_matriculate'),
    path('idr-idm/get-all-localisation/', views.gat_all_localisation, name='gat_all_localisation'),
    path('idr-idm/get-all-breakdown/', views.get_all_breakdown, name='get_all_breakdown'),
    path('idr-idm/file-upload/', views.upload_file, name='upload_file'),
    path('idr-idm/get-file-jointe/', views.get_file_jointe, name='get_file_jointe'),
    path('idr-idm/delete-file-jointe/', views.delete_jointe, name='delete_jointe'),
    path('idr-idm/delete-breakdown/', views.delete_breakdown, name='delete_breakdown'),
    path('idr-idm/get-machines/', views.get_machines, name='get_machines'),
    path('idr-idm/get-breakdown/', views.get_all_machineidridm_with_breakdown_false, name='get_breakdown'),
    path('get-all-client/', views.get_all_client, name='get_all_client'),
    path('add-client/', views.add_client, name='add_client'),
    path('delete-client/<str:uid>/', views.delete_client, name='delete_client'),

]
