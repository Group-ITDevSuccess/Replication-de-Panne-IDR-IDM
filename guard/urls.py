from django.urls import path

from . import views

app_name = 'guard'
urlpatterns = [
    path('login/', views.LoginLDAP.as_view(), name='login'),
    path('logout/', views.logout_ldap, name='logout'),
    path('administrations/', views.index, name='index'),
    path('get-all-permission/', views.get_all_permission, name='get_all_permission'),
    path('administrations/get-all-users/', views.all_users_json, name='get_all_users_json'),
    path('administrations/get-all-client-not-used/', views.get_all_client_not_used_json,
         name='get_all_client_not_used_json'),
    path('administrations/get-all-client-used/', views.get_all_client_used_json, name='get_all_client_used_json'),
    path('administrations/update-status-client/', views.update_status_client, name='update_status_client'),
    path('administrations/update-user/', views.update_user_json, name='update_user_json'),
    path('administrations/create-user/', views.create_user_json, name='create_user_json'),
    path('administrations/delete-user/', views.delete_user_json, name='delete_user_json'),
]
