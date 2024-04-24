from django.urls import path
from . import views

app_name = 'detail'
urlpatterns = [
    path('/client/<str:uid>/', views.index, name='index')
]
