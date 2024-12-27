from django.conf import settings
from django.db import models

from common.base_models import TenantIsolationMixIn, TimestampModel


class TenantUser(models.Model):
    tenant = models.ForeignKey("core.Tenant", on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)


class Tenant(TimestampModel):
    domain = models.SlugField(unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name or self.domain

    def check_user(self, user):
        return TenantUser.objects.filter(user=user, tenant=self).exists()


class Organization(TenantIsolationMixIn):
    name = models.CharField(max_length=255)
    details = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Department(TenantIsolationMixIn):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    details = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Customer(TenantIsolationMixIn):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return
