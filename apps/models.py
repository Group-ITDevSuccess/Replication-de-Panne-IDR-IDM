import json

from django.db import models
import uuid


class BaseModel(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Company(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Machine(BaseModel):
    matriculate = models.CharField(max_length=100, unique=True)
    model = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.matriculate


class Location(BaseModel):
    name = models.CharField(max_length=255)
    details = models.JSONField()

    def save(self, *args, **kwargs):
        # Convertir le dictionnaire en chaîne JSON avant de sauvegarder
        if isinstance(self.details, dict):
            self.details = json.dumps(self.details)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Client(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=25)
    location = models.ForeignKey('Location', on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return self.name


class Breakdown(BaseModel):
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    machine = models.ForeignKey('Machine', on_delete=models.CASCADE)
    location = models.ForeignKey('Location', on_delete=models.CASCADE, blank=True, null=True)
    client = models.ForeignKey('Client', on_delete=models.CASCADE, blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True, verbose_name='Start Breakdown')
    end = models.DateTimeField(blank=True, null=True, verbose_name='End Breakdown')
    appointment = models.DateField(blank=True, null=True, verbose_name='Request Appointment')
    enter = models.DateField(blank=True, null=True, verbose_name='Enter Garage')
    exit = models.DateField(blank=True, null=True, verbose_name='Exit Garage')
    leave = models.DateField(blank=True, null=True, verbose_name='Leave Garage')
    order = models.IntegerField(null=True, blank=True, verbose_name='Order Repair')
    works = models.TextField(blank=True, null=True, verbose_name='Work Request')

    def __str__(self):
        return f"{self.machine}"
