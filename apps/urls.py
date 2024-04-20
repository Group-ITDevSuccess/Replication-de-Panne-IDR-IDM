from django.urls import path
from . import views

app_name = 'apps'
urlpatterns = [
    path('', views.index, name='index'),
    path('post-line-data/', views.post_line, name='post_line'),
    path('update-line-data/', views.update_line, name='update_line'),
    path('create-machine/', views.create_machine, name='create_machine'),
    path('get-all-machines-in-table/', views.get_all_machines_in_table, name='get_all_machines_in_table'),
    path('get-all-matriculate/', views.get_all_matriculate, name='get_all_matriculate'),
    path('get-all-localisation/', views.gat_all_localisation, name='gat_all_localisation'),
    path('get-all-breakdown/', views.get_all_breakdown, name='get_all_breakdown'),
    path('file-upload/', views.upload_file, name='upload_file'),
    path('get-file-jointe/', views.get_file_jointe, name='get_file_jointe'),
    path('delete-file-jointe/', views.delete_jointe, name='delete_jointe'),
    path('delete-breakdown/', views.delete_breakdown, name='delete_breakdown'),
    path('get-machines/', views.get_machines, name='get_machines'),
    path('get-breakdown/', views.get_all_machine_with_breakdown_false, name='get_breakdown'),

]
