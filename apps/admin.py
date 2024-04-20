from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin

from .models import Machine, Client, Breakdown, Localisation


class LocalisationResource(resources.ModelResource):
    class Meta:
        model = Localisation
        fields = ('uid', 'latitude', 'longitude', 'locality', 'commune', 'district', 'region')
        export_order = ('uid', 'latitude', 'longitude', 'locality', 'commune', 'district', 'region')
        import_id_fields = ['uid']


@admin.register(Localisation)
class LocalisationAdmin(ImportExportModelAdmin):
    resource_class = LocalisationResource
    list_display = ('locality', 'commune', 'district', 'region')
    list_display_links = ('locality', 'commune',)
    search_fields = ('locality', 'commune', 'district', 'region')
    list_filter = ('commune', 'district', 'region')


# Custom fieldsets for each model
company_fieldsets = (
    (None, {
        'fields': ('name', 'description')
    }),
    ('Dates', {
        'fields': ('created_at', 'updated_at'),
        'classes': ('collapse',)  # Hide this section by default
    }),
)

machine_fieldsets = (
    (None, {
        'fields': ('matriculate', 'model',  'breakdown')
    }),
    ('Dates', {
        'fields': ('created_at', 'updated_at'),
        'classes': ('collapse',)  # Hide this section by default
    }),
)

localisation_fieldsets = (
    (None, {
        'fields': ('name', 'details')
    }),
    ('Dates', {
        'fields': ('created_at', 'updated_at'),
        'classes': ('collapse',)  # Hide this section by default
    }),
)

client_fieldsets = (
    (None, {
        'fields': ('name', 'email', 'phone')
    }),
    ('Dates', {
        'fields': ('created_at', 'updated_at'),
        'classes': ('collapse',)  # Hide this section by default
    }),
)

breakdown_fieldsets = (
    (None, {
        'fields': (
            'localisation', 'client', 'start', 'archived', 'appointment', 'enter', 'order', 'prevision', 'piece', 'diagnostics',
            'achats', 'imports', 'decision')
    }),
    ('Dates', {
        'fields': ('created_at', 'updated_at'),
        'classes': ('collapse',)  # Hide this section by default
    }),
)


# Register models with custom fieldsets

@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    fieldsets = machine_fieldsets
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('breakdown',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    fieldsets = client_fieldsets
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Breakdown)
class BreakdownAdmin(admin.ModelAdmin):
    fieldsets = breakdown_fieldsets
    readonly_fields = ('created_at', 'updated_at')
