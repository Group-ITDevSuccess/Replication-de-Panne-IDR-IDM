from django.urls import path

from . import views

app_name = 'guard'
urlpatterns = [
    path('login/', views.LoginLDAP.as_view(), name='login'),
    path('logout/', views.logout_ldap, name='logout'),
    path('administrations/', views.index, name='index'),
    path('administrations/get-all-users/', views.all_users_json, name='get_all_users_json'),
    path('administrations/update-user/', views.update_user_json, name='update_user_json'),
]
