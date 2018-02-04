from getpass import getpass

import json
import readline
import requests

from configuration import C
from directory import Directory
from user import User
from password import Password

class Club:
    def __init__(self, club=None, client=None, secret=None):
        self._club = club
        self._client = client
        self._secret = secret
        self._token = None
        self.escalate()

    def authenticate(self, username, password):
        response = requests.post(
            "https://accounts.tidyhq.com/oauth/token",
            {
                "grant_type": "password",
                "domain_prefix": self._club,
                "client_id": self._client,
                "client_secret": self._secret,
                "username": username,
                "password": password,
            }
        )
        response.raise_for_status()
        self._token = response.json()["access_token"]

    def escalate(self):
        response = requests.post(
            "https://accounts.tidyhq.com/oauth/token",
            {
                "grant_type": "password",
                "domain_prefix": self._club,
                "client_id": self._client,
                "client_secret": self._secret,
                "username": C.TIDY_MANAGER,
                "password": C.TIDY_PASSWORD,
            }
        )
        response.raise_for_status()
        self._token_root = response.json()["access_token"]

    def me(self):
        return Contact(self)

class Contact:
    def __init__(self, parent, id=None):
        self._parent = parent
        response = requests.get(
            "https://api.tidyhq.com/v1/contacts/me"
            if id is None
            else "https://api.tidyhq.com/v1/contacts/%d" % id,
            params={
                "access_token": (
                    self._parent._token
                    if id is None
                    else self._parent._token_root
                )
            }
        )
        response.raise_for_status()
        self._data = response.json()

    def membership(self):
        response = requests.get(
            "https://api.tidyhq.com/v1/contacts/%d/memberships"
            % self._data["id"],
            params={
                "active": "true",
                "access_token": self._parent._token_root
            }
        )
        response.raise_for_status()
        memberships = response.json()
        return None if len(memberships) < 1 else memberships[0]

    def username(self, new=None):
        if new is None:
            fields = self._data["custom_fields"]
            field = [x for x in fields if x["id"] == C.TIDY_USERNAME_FIELD]
            value = "" if len(field) < 1 else field[0]["value"]
            return None if len(value) < 1 else value
        else:
            response = requests.put(
                "https://api.tidyhq.com/v1/contacts/%d"
                % self._data["id"],
                params={
                    "access_token": self._parent._token_root
                },
                headers={
                    "content-type": "application/json"
                },
                data=json.dumps({
                    "custom_fields": [{
                        "id": C.TIDY_USERNAME_FIELD,
                        "value": new
                    }]
                })
            )
            response.raise_for_status()
