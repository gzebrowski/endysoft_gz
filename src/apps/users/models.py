# -*- coding:utf-8 -*-

from typing import Optional

from django.contrib.auth import authenticate  # , logout, login
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import ValidationError, validate_email
from rest_framework.authtoken.models import Token


class AppUserManager(UserManager):
    @classmethod
    def normalize_email(cls, email):
        if not email:
            return None
        return email.strip().lower()

    def create_user(self, username: Optional[str] = None, email: Optional[str] = None, password: Optional[str] = None,
                    **extra_fields):
        if "is_active" not in extra_fields:
            extra_fields["is_active"] = False
        username, email = self._prepare_login_fields(username, email)
        return super().create_user(username, email, password, **extra_fields)

    def _prepare_login_fields(self, username, email):
        try:
            validate_email(username)
        except ValidationError:
            pass
        else:
            if not email:
                email = username
        if not username and email:
            username = email
        return username, email

    def create_superuser(
        self, username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        **extra_fields,
    ):
        extra_fields["is_active"] = True
        username, email = self._prepare_login_fields(username, email)
        return super().create_superuser(
            username, email, password, **extra_fields
        )


class AppUser(AbstractUser):
    REQUIRED_FIELDS = []
    USERNAME_FIELD = "email"
    objects = AppUserManager()

    def __str__(self):
        return "%s" % self.username

    @classmethod
    def check_credentials(cls, email=None, password=None, token=None):
        user = None
        if token:
            user = authenticate(user_hash=token)
        elif email and password:
            user = authenticate(username=email, password=password)
        return user

    @property
    def user_auth_token(self):
        try:
            return str(self.auth_token.key)
        except Token.DoesNotExist:
            return str(self.generate_api_key())

    def generate_api_key(self):
        try:
            token = self.auth_token
        except Token.DoesNotExist:
            token = Token.objects.create(user=self)
        else:
            token.delete()
            token = Token.objects.create(user=self)
        return token


AppUser._meta.get_field("email")._unique = True
username_field = AppUser._meta.get_field("username")
username_field._unique = False
username_field.blank = True
username_field.max_length = 255
