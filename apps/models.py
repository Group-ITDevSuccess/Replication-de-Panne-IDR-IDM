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


class Client(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=25)
    localisation = models.ForeignKey('Localisation', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name


class Localisation(BaseModel):
    latitude = models.DecimalField(decimal_places=10, max_digits=20, null=True, blank=True)
    longitude = models.DecimalField(decimal_places=10, max_digits=20, null=True, blank=True)
    locality = models.CharField(max_length=100)
    commune = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    region = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.locality}, {self.commune}, {self.district}"

    class Meta:
        ordering = ['commune', 'locality']


class Breakdown(BaseModel):
    machine = models.ForeignKey('Machine', on_delete=models.CASCADE)
    localisation = models.ForeignKey('Localisation', on_delete=models.CASCADE, blank=True, null=True)
    client = models.ForeignKey('Client', on_delete=models.CASCADE, blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True, verbose_name='Start Breakdown')
    appointment = models.DateTimeField(blank=True, null=True, verbose_name='Request Appointment')
    enter = models.DateTimeField(blank=True, null=True, verbose_name='Enter Garage')
    leave = models.DateTimeField(blank=True, null=True, verbose_name='Leave Garage')
    order = models.IntegerField(null=True, blank=True, verbose_name='Order Repair')
    works = models.TextField(blank=True, null=True, verbose_name='Work Request')
    prevision = models.TextField(blank=True, null=True, verbose_name='Exit Garage Prevision')
    piece = models.TextField(blank=True, null=True, verbose_name='Etat Piece')
    decision = models.TextField(blank=True, null=True, verbose_name='Decision')
    diagnostics = models.TextField(blank=True, null=True, verbose_name='Diagnostics & Commentaire SAV')
    achats = models.TextField(blank=True, null=True, verbose_name='Commentaire Achats')
    imports = models.TextField(blank=True, null=True, verbose_name='Commentaire Import')

    def __str__(self):
        return f"{self.machine}"
