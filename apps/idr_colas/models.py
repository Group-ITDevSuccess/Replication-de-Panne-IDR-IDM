from django.db import models

from apps.idr_idm.models import BaseModel, Localisation, Client, Jointe, Historic


class MachineIdrColas(BaseModel):
    matriculate = models.CharField(max_length=100, unique=True)
    model = models.CharField(max_length=150)
    breakdown = models.ManyToManyField('BreakdownIdrColas', blank=True)

    def __str__(self):
        return self.matriculate

    def has_active_breakdown(self):
        return self.breakdown.filter(archived=False).exists()


class BreakdownIdrColas(BaseModel):
    MONTH = [
        ('Janvier', 'Janvier'),
        ('Fevrier', 'Février'),
        ('Mars', 'Mars'),
        ('Avril', 'Avril'),
        ('Mai', 'Mai'),
        ('Juin', 'Juin'),
        ('Juillet', 'Juillet'),
        ('Aout', 'Août'),
        ('Septembre', 'Septembre'),
        ('Octobre', 'October'),
        ('Novembre', 'Novembre'),
        ('Decembre', 'Décembre')
    ]
    month = models.CharField(choices=MONTH, null=True, blank=True, max_length=50)
    jde = models.CharField(choices=MONTH, null=True, blank=True, max_length=150)
    localisation = models.ForeignKey(Localisation, on_delete=models.CASCADE, blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, blank=True, null=True)
    start = models.DateTimeField(blank=True, null=True, verbose_name='Start Breakdown')
    end = models.DateTimeField(blank=True, null=True, verbose_name='Leave Garage')
    prevision = models.DateTimeField(blank=True, null=True, verbose_name='Leave Garage')
    archived = models.BooleanField(default=False)
    works = models.TextField(blank=True, null=True, verbose_name='Work Request')
    commentaire = models.TextField(blank=True, null=True, verbose_name='Commentaire')
    jointe = models.ManyToManyField(Jointe, blank=True, verbose_name='Piece Jointe')
    historic = models.ManyToManyField(Historic, blank=True, verbose_name='Historique Breakdown')

    def __str__(self):
        return f"{self.created_at} | {self.client}"
