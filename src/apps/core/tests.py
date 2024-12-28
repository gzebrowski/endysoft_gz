from typing import Type

from django.db.models import Model
from django.shortcuts import reverse
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN)

from apps.core.models import Department, Organization, Tenant, TenantUser
from apps.users.models import AppUser


def test_create_tenant(db, api_client, user1, user2):
    create_tenant_url = reverse("api:tenants_url-list")
    data_create1 = {"name": "Tenant 1", "domain": "tenant1"}
    data_create2 = {"name": "Tenant 2", "domain": "tenant2"}
    assert TenantUser.objects.all().count() == 0
    response = api_client.post(create_tenant_url, data_create1)
    assert response.status_code == HTTP_401_UNAUTHORIZED
    response = api_client.post(create_tenant_url, data_create1, HTTP_AUTHORIZATION="Token " + user1.user_auth_token)
    assert response.status_code == HTTP_201_CREATED
    response = api_client.post(create_tenant_url, data_create2, HTTP_AUTHORIZATION="Token " + user2.user_auth_token)
    assert response.status_code == HTTP_201_CREATED
    response = api_client.post(create_tenant_url, data_create1, HTTP_AUTHORIZATION="Token " + user1.user_auth_token)
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert TenantUser.objects.filter(user=user1, tenant__domain="tenant1").count() == 1
    assert TenantUser.objects.filter(user=user2, tenant__domain="tenant2").count() == 1


def _get_cases(user: AppUser, tenant: Tenant, bad_tenant: Tenant, ok_code: int, good_cases_first=False):
    """
    this helper function is used to generate security test cases for the API calls

    :param user: the user that has access to the tenant
    :param tenant: some tenant that the user has access to
    :param bad_tenant: some tenant that the user does not have access to
    :param ok_code: good response codes can differ and can be HTTP_200_OK or HTTP_201_CREATED or HTTP_204_NO_CONTENT
    :param good_cases_first: normally we want to test the bad cases first, but sometimes we don't want that
    :return: list of tuples with kwargs and expected response codes
    """
    cases = [
        ({'user': user}, HTTP_400_BAD_REQUEST),
        ({}, HTTP_400_BAD_REQUEST),
        ({"user": user, "domain": bad_tenant.domain}, HTTP_403_FORBIDDEN),
        ({"user": user, "domain": tenant.domain}, ok_code),
    ]
    if good_cases_first:
        cases = cases[::-1]
    return cases


def _check_section(api_tenant_client, user1, user2, tenant1: Tenant, tenant2: Tenant, router_key: str,
                   model_cls: Type[Model], create_cases=None, rud_cases=None, url_extra_args=None):
    """
    this helper function is used to test the CRUD operations for the model
    :param api_tenant_client:
    :param user1:
    :param user2:
    :param tenant1:
    :param tenant2:
    :param router_key:
    :param model_cls:
    :param create_cases:
    :param rud_cases: [read, update, delete] cases
    :return:
    """
    # we want to get char fields from model to prepare fake data - for Organization it is name and details, etc.
    char_fields = [f.name for f in model_cls._meta.get_fields() if f.get_internal_type() == 'CharField']
    url_extra_args = url_extra_args or []
    list_objects_url = reverse(f"api:{router_key}-list", args=url_extra_args)
    # here we want to create objects
    for create_case in create_cases:
        for kwargs, expected_response_code in create_case['cases']:
            response = api_tenant_client.post(list_objects_url, create_case['data'], **kwargs)
            assert response.status_code == expected_response_code
    # here we want to list, get, update and delete objects
    for scenario in rud_cases:
        for kwargs, expected_response_code in scenario['cases']:
            response = api_tenant_client.get(list_objects_url, **kwargs)
            assert response.status_code == expected_response_code
            if expected_response_code == HTTP_200_OK:
                response_data = response.json()
                assert len(response_data) == scenario['expected_count']
                for response_item in response_data:
                    update_url = reverse(f"api:{router_key}-detail", args=url_extra_args + [response_item['id']])
                    # now testing retrieve and update
                    for case_kws, case_code in scenario['cases']:
                        get_resp = api_tenant_client.get(update_url, **case_kws)
                        assert get_resp.status_code == case_code
                        new_data = {k: v + "Updated!!!" for k, v in response_item.items() if k in char_fields}
                        put_resp = api_tenant_client.put(update_url, new_data, **case_kws)
                        assert put_resp.status_code == case_code
                        if case_code == HTTP_200_OK:
                            curr_obj = model_cls.objects.get(pk=response_item['id'])
                            for c_field in char_fields:
                                assert new_data[c_field] == getattr(curr_obj, c_field)
                    # now testing delete
                    for case_kws, case_code in scenario['cases']:
                        del_resp = api_tenant_client.delete(update_url, **case_kws)
                        assert del_resp.status_code == (HTTP_204_NO_CONTENT if case_code == HTTP_200_OK else case_code)
                        if case_code == HTTP_200_OK:
                            assert not model_cls.objects.filter(pk=response_item['id']).exists()


def test_organizations(db, api_tenant_client, user1, user2, tenant1, tenant2):
    char_fields = [f.name for f in Organization._meta.get_fields() if f.get_internal_type() == 'CharField']

    def _fake_data(nr: int):
        # for Organization it will be {'name': 'organization 1', 'details': 'details 1'} when nr is 1 etc.
        return {k: f"{k} {nr}" for k in char_fields}

    create_cases = [
        {'data': _fake_data(1), 'cases': _get_cases(user1, tenant1, tenant2, HTTP_201_CREATED)},
        {'data': _fake_data(2), 'cases': _get_cases(user1, tenant1, tenant2, HTTP_201_CREATED)},
        {'data': _fake_data(3), 'cases': _get_cases(user2, tenant2, tenant1, HTTP_201_CREATED)},
    ]
    rud_cases = [
        {'cases': _get_cases(user1, tenant1, tenant2, HTTP_200_OK), 'expected_count': 2},
        {'cases': _get_cases(user2, tenant2, tenant1, HTTP_200_OK), 'expected_count': 1},
    ]
    _check_section(api_tenant_client, user1, user2, tenant1, tenant2, 'organizations_url', Organization, create_cases,
                   rud_cases)


def test_departments(db, api_tenant_client, user1, user2, tenant1, tenant2, organization1_tenant1,
                     organization2_tenant1, organization1_tenant2):
    char_fields = [f.name for f in Department._meta.get_fields() if f.get_internal_type() == 'CharField']

    def _fake_data(nr: int, organization: Organization):
        # for Organization it will be {'name': 'organization 1', 'details': 'details 1'} when nr is 1 etc.
        result = {k: f"{k} {nr}" for k in char_fields}
        result['organization'] = organization.pk
        return result

    create_cases = [
        {'data': _fake_data(1, organization1_tenant1), 'cases': _get_cases(user1, tenant1, tenant2, HTTP_201_CREATED)},
        {'data': _fake_data(2, organization1_tenant1), 'cases': _get_cases(user1, tenant1, tenant2, HTTP_201_CREATED)},
        {'data': _fake_data(3, organization1_tenant2), 'cases': _get_cases(user2, tenant2, tenant1, HTTP_201_CREATED)},
    ]
    rud_cases = [
        {'cases': _get_cases(user1, tenant1, tenant2, HTTP_200_OK), 'expected_count': 2},
        {'cases': _get_cases(user2, tenant2, tenant1, HTTP_200_OK), 'expected_count': 1},
    ]
    _check_section(api_tenant_client, user1, user2, tenant1, tenant2, 'departments_url', Department, create_cases,
                   rud_cases, [organization1_tenant1.pk])
