from django.contrib import admin

from .models import CustomUser, CustomPermission


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'autoriser')
    list_filter = ('autoriser',)
    list_editable = ('autoriser',)
    search_fields = ('username', 'email')
    fieldsets = (
        (None, {'fields': ('username',)}),
        ('Informations personnelles',
         {'fields': [
             ('first_name', 'last_name'), ('email',)]}
         ),
        ('Permissions', {
            "classes": ("collapse", "expanded"),
            'fields': (
                'autoriser', 'is_active', 'is_staff', 'is_superuser',
            )}),
        ('Action permise', {
            "classes": ("collapse",),
            'fields': ['groups', 'user_permissions']
        }),
        ('Dates importantes', {"classes": ("collapse",), 'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('username', 'last_login', 'date_joined')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )


@admin.register(CustomPermission)
class CustomPermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')  # Colonnes à afficher dans la liste des objets CustomPermission
    search_fields = ('name',)  # Champs à utiliser pour la recherche dans l'interface d'administration
