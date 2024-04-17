import uuid

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy


class CustomUser(AbstractUser):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    autoriser = models.BooleanField(
        default=False,
        help_text=gettext_lazy("Autoriser l'utilisateur à se connecter au plateforme.")
    )

    groups = models.ManyToManyField(Group, blank=True, related_name='custom_users')
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name='custom_users')
    custom_permissions = models.ManyToManyField('CustomPermission', blank=True, related_name='custom_users')

    def __str__(self):
        return self.username

    def get_all_permissions(self, obj=None):
        permissions = super().get_all_permissions(obj=obj)
        custom_permissions = self.custom_permissions.all()
        permissions |= set(custom_permissions)
        return permissions

    class Meta:
        verbose_name = 'Authentification et Sécurité'
        verbose_name_plural = 'Authentification'


class CustomPermission(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Permission personnalisée'
        verbose_name_plural = 'Permissions personnalisées'
