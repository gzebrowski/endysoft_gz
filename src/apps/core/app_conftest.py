import pytest
from django.conf import settings
from apps.core.models import Tenant, TenantUser, Organization, Department


@pytest.fixture
def tenant1(db, user1):
    tn1 = Tenant.objects.create(name="Tenant 1", domain='tenant1')
    TenantUser.objects.create(tenant=tn1, user=user1)
    return tn1


@pytest.fixture
def tenant2(db, user2):
    tn2 = Tenant.objects.create(name="Tenant 2", domain='tenant2')
    TenantUser.objects.create(tenant=tn2, user=user2)
    return tn2


class ApiWrapper:
    def __init__(self, api_client):
        self.api_client = api_client
        self._method = None

    def __getattr__(self, item):
        methods = ["get", "post", "put", "delete", "patch"]
        if item in methods:
            self._method = item
            return self
        return getattr(self.api_client, item)

    def __call__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        domain = kwargs.pop("domain", None)
        if user:
            kwargs["HTTP_AUTHORIZATION"] = "Token " + user.user_auth_token
        if domain:
            kwargs["HTTP_" + settings.TENANT_HEADER.replace('-', '_').upper()] = domain
        return getattr(self.api_client, self._method)(*args, **kwargs)


@pytest.fixture
def api_tenant_client(api_client):
    return ApiWrapper(api_client)


@pytest.fixture
def organization1_tenant1(tenant1):
    return Organization.objects.create(
        name="Organization 1/1",
        details="Details 1/1",
        tenant_id=tenant1.pk,
    )


@pytest.fixture
def organization2_tenant1(tenant1):
    return Organization.objects.create(
        name="Organization 2/1",
        details="Details 2/1",
        tenant_id=tenant1.pk,
    )


@pytest.fixture
def organization1_tenant2(tenant2):
    return Organization.objects.create(
        name="Organization 1/2",
        details="Details 1/2",
        tenant_id=tenant2.pk,
    )
