from django.urls import path
from . import views

app_name = 'idr_colas'
urlpatterns = [
    path('', views.index, name='index'),
    path('idr-colas/post-line-data/', views.post_line, name='post_line'),
    path('idr-colas/update-line-data/', views.update_line, name='update_line'),
    path('idr-colas/create-machine/', views.create_machine, name='create_machine'),
    path('idr-colas/get-all-machines-in-table/', views.get_all_machines_in_table, name='get_all_machines_in_table'),
    path('idr-colas/get-all-matriculate/', views.get_all_matriculate, name='get_all_matriculate'),
    path('idr-colas/get-all-localisation/', views.gat_all_localisation, name='gat_all_localisation'),
    path('idr-colas/get-all-breakdown/', views.get_all_breakdown, name='get_all_breakdown'),
    path('idr-colas/file-upload/', views.upload_file, name='upload_file'),
    path('idr-colas/get-file-jointe/', views.get_file_jointe, name='get_file_jointe'),
    path('idr-colas/delete-file-jointe/', views.delete_jointe, name='delete_jointe'),
    path('idr-colas/delete-breakdown/', views.delete_breakdown, name='delete_breakdown'),
    path('idr-colas/get-machines/', views.get_machines, name='get_machines'),
    path('idr-colas/get-breakdown/', views.get_all_machineidrcolas_with_breakdown_false, name='get_breakdown'),

]
