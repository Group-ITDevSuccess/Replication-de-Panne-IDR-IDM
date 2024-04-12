from django.urls import path
from . import views

app_name = 'apps'
urlpatterns = [
    path('', views.index, name='index'),
    path('create-machine/', views.create_machine, name='create_machine'),
    path('get-all-machines/', views.get_all_machines, name='get_all_machines'),
    path('get-machines/<str:company>/', views.get_machines, name='get_machines'),
]
