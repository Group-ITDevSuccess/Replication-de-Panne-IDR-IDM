from django.urls import path
from . import views

app_name = 'apps'
urlpatterns = [
    path('', views.index, name='index'),
    path('create-machine/', views.create_machine, name='create_machine'),
    path('get-all-machines-in-table/', views.get_all_machines_in_table, name='get_all_machines_in_table'),
    path('get-all-companies/', views.get_all_companies, name='get_all_companies'),
    path('get-all-matriculate/', views.get_all_matriculate, name='get_all_matriculate'),
    path('get-all-localisation/', views.gat_all_localisation, name='gat_all_localisation'),
    path('get-all-breakdown/', views.get_all_breakdown, name='get_all_breakdown'),
    path('post-line/', views.post_line, name='post_line'),
    path('update-line/', views.update_line, name='update_line'),
    path('delete-breakdown/', views.delete_breakdown, name='delete_breakdown'),
    path('get-machines/', views.get_machines, name='get_machines'),
    path('get-breakdown/<str:company>/', views.get_breakdown, name='get_breakdown'),

]
