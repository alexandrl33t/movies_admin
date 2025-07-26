import http
import json
from enum import StrEnum, auto
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class Roles(StrEnum):
    ADMIN = "admin"
    SUBSCRIBER = "subscriber"
    DEFAULT = "default"


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        login_url = urljoin(settings.AUTH_API, "/api/auth/login")
        payload = {'email': username, 'password': password}
        try:
            response = requests.post(login_url, data=json.dumps(payload))
            if response.status_code != http.HTTPStatus.OK:
                return None
            data = response.json()
            access_token = data.get('access_token')

            user_details_url = urljoin(settings.AUTH_API, "/api/auth/user-details")
            response = requests.get(user_details_url, headers={'Authorization': 'Bearer ' + access_token})
            if response.status_code != http.HTTPStatus.OK:
                return None
            data = response.json()
            user, created = User.objects.get_or_create(email=data['email'])
            user.set_password(password)
            roles = data.get('roles')
            if Roles.ADMIN in roles:
                user.is_staff = True
                user.is_admin = True
            user.save()
        except Exception:
            return None
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
