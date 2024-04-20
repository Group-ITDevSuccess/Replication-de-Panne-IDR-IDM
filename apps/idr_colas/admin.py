from django.contrib import admin
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin

from .models import MachineIdrColas, BreakdownIdrColas



machine_fieldsets = (
    (None, {
        'fields': ('matriculate', 'model', 'breakdown')
    }),
    ('Dates', {
        'fields': ('created_at', 'updated_at'),
        'classes': ('collapse',)  # Hide this section by default
    }),
)

breakdown_fieldsets = (
    (None, {
        'fields': (
            'localisation', 'client', 'start', 'archived', 'end', 'prevision',
            'commentaire')
    }),
    ('Dates', {
        'fields': ('created_at', 'updated_at'),
        'classes': ('collapse',)  # Hide this section by default
    }),
)


# Register models with custom fieldsets

@admin.register(MachineIdrColas)
class MachineAdmin(admin.ModelAdmin):
    fieldsets = machine_fieldsets
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('breakdown',)


@admin.register(BreakdownIdrColas)
class BreakdownAdmin(admin.ModelAdmin):
    fieldsets = breakdown_fieldsets
    readonly_fields = ('created_at', 'updated_at')
