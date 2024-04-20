from django.urls import path
from . import views

app_name = "idr_colas"
urlpatterns = [
    path('', views.index, name='index')
]
