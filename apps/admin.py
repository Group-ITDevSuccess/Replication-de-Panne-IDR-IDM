from django.contrib import admin
from .models import Company, Machine, Location, Client, Breakdown

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
        'fields': ('matriculate', 'model', 'description', 'company')
    }),
    ('Dates', {
        'fields': ('created_at', 'updated_at'),
        'classes': ('collapse',)  # Hide this section by default
    }),
)

location_fieldsets = (
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
        'fields': ('name', 'email', 'phone', 'location')
    }),
    ('Dates', {
        'fields': ('created_at', 'updated_at'),
        'classes': ('collapse',)  # Hide this section by default
    }),
)

breakdown_fieldsets = (
    (None, {
        'fields': ('company', 'machine', 'location', 'client', 'start', 'end', 'appointment', 'enter', 'exit', 'order')
    }),
    ('Dates', {
        'fields': ('created_at', 'updated_at'),
        'classes': ('collapse',)  # Hide this section by default
    }),
)


# Register models with custom fieldsets
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    fieldsets = company_fieldsets
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    fieldsets = machine_fieldsets
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    fieldsets = location_fieldsets
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    fieldsets = client_fieldsets
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Breakdown)
class BreakdownAdmin(admin.ModelAdmin):
    fieldsets = breakdown_fieldsets
    readonly_fields = ('created_at', 'updated_at')
