from django.shortcuts import reverse
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED

from apps.users.models import AppUser


def test_signup_and_signin(db, api_client):
    data = {
        'email': 'user1@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'password': 'password',
    }
    url = reverse('api:users_url-signup')
    response = api_client.post(url, data)
    assert response.status_code == HTTP_201_CREATED
    user = AppUser.objects.get(email=data['email'])
    assert (user.first_name, user.last_name) == (data['first_name'], data['last_name'])
    assert user.check_password(data['password'])
    assert 'token' in response.json()

    data_items = [
        ({'email': 'user2@example.com', 'password': data['password']}, HTTP_401_UNAUTHORIZED),
        ({'email': data['email'], 'password': 'wrong_password'}, HTTP_401_UNAUTHORIZED),
        ({'email': data['email'], 'password': data['password']}, HTTP_200_OK),
    ]
    url = reverse('api:users_url-login')
    for login_data, expected_code in data_items:
        response = api_client.post(url, login_data)
        assert response.status_code == expected_code
        if expected_code == HTTP_200_OK:
            assert 'token' in response.json()
            assert response.json()['token'] == user.user_auth_token

