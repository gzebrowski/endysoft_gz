import pytest

from apps.users.models import AppUser


@pytest.fixture
def user1(db):
    return AppUser.objects.create_user(
        is_active=True,
        email="user1@example.com",
        first_name="John",
        last_name="Doe",
    )


@pytest.fixture
def user2(db):
    return AppUser.objects.create_user(
        is_active=True,
        email="user2@example.com",
        first_name="Alice",
        last_name="Smith",
    )
