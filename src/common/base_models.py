from django.db import models


class TimestampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TenantIsolationManager(models.Manager):
    def create(self, tenant_id=None, **kwargs):
        assert tenant_id, "tenant_id is required"
        kwargs['tenant_id'] = tenant_id
        return super().create(**kwargs)


class TenantIsolationMixIn(TimestampModel):
    tenant_id = models.IntegerField(editable=False)
    objects = TenantIsolationManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.tenant_id:
            raise ValueError("tenant_id is required")
        super().save(*args, **kwargs)
