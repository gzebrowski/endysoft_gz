from django.shortcuts import reverse
from apps.core.models import TenantUser


def test_create_tenant(db, api_client, user1, user2):
    create_tenant_url = reverse("api:tenants_url-list")
    data_create1 = {"name": "Tenant 1", "domain": "tenant1"}
    data_create2 = {"name": "Tenant 2", "domain": "tenant2"}
    assert TenantUser.objects.all().count() == 0
    response = api_client.post(create_tenant_url, data_create1)
    assert response.status_code == 401
    response = api_client.post(create_tenant_url, data_create1, HTTP_AUTHORIZATION="Token " + user1.user_auth_token)
    assert response.status_code == 201
    response = api_client.post(create_tenant_url, data_create2, HTTP_AUTHORIZATION="Token " + user2.user_auth_token)
    assert response.status_code == 201
    response = api_client.post(create_tenant_url, data_create1, HTTP_AUTHORIZATION="Token " + user1.user_auth_token)
    assert response.status_code == 400
    assert TenantUser.objects.filter(user=user1, tenant__domain="tenant1").count() == 1
    assert TenantUser.objects.filter(user=user2, tenant__domain="tenant2").count() == 1


def test_organizations(db, api_tenant_client, user1, user2, tenant1, tenant2):
    list_organization_url = reverse("api:organizations_url-list")
    organizations_data = [
        {'data': {"name": "Organization 1", "details": "Details 1"}, 'cases': [
            ({'user': user1, 'domain': tenant2.domain}, 403),
            ({}, 400),
            ({'user': user1}, 400),
            ({'user': user1, 'domain': tenant1.domain}, 201),
        ]},
        {'data': {"name": "Organization 2", "details": "Details 2"}, 'cases': [
            ({'user': user2, 'domain': tenant1.domain}, 403),
            ({}, 400),
            ({'user': user2}, 400),
            ({'user': user2, 'domain': tenant2.domain}, 201),
            ]
         }]
    for organization_data in organizations_data:
        for kwargs, response_code in organization_data['cases']:
            response = api_tenant_client.post(list_organization_url, organization_data['data'], **kwargs)
            assert response.status_code == response_code
    scenarios_of_kwargs_and_responses = [
        ({'user': user1, 'domain': tenant1.domain}, 200),
        ({'user': user2, 'domain': tenant2.domain}, 200),
        ({}, 400),
        ({'user': user1}, 400),
        ({'user': user1, 'domain': tenant2.domain}, 403),
    ]
    for kwargs, response_code in scenarios_of_kwargs_and_responses:
        response = api_tenant_client.get(list_organization_url, **kwargs)
        assert response.status_code == response_code
        if response_code == 200:
            assert len(response.json()) == 1
