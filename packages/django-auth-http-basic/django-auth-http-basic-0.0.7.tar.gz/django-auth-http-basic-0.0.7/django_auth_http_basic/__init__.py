# -*- coding: utf-8 -*-

"""Simple authenticaton backend based on HTTP basic authentication.

:copyright: (c) 2016 by Detlef Stern
:license: Apache 2.0, see LICENSE
"""

import logging

import requests

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.conf import settings


LOGGER = logging.getLogger(__name__)


class HttpBasicAuthBackend(ModelBackend):
    """Authentication backend that uses HTTP basic authentication.

    In all other aspects this backend should behave like the default
    model-based backend from Django.
    """

    @staticmethod
    def checkpw_basic_auth(url, username, password):
        """Check authentication via HTTP basic authentication."""
        LOGGER.debug("Basic-auth URL=%s, user=%s", url, username)
        if url is None:
            return True

        try:
            response = requests.head(url, auth=(username, password))
            status_code = response.status_code
            LOGGER.debug('Basic-auth Status-Code=%d', status_code)
            return 200 <= status_code <= 299
        except requests.RequestException:
            LOGGER.exception(
                "Unable to get authentication from '%s' for user '%s':",
                url, username)
            return None

    def authenticate(
            self, request=None, username=None, password=None, **kwargs):
        """Authenticate with an user name and a password.

        Requires a setting HTTP_BASIC_AUTH_URL for specifying the URL endpoint
        for checking user name / password. URL can be set to None for testing
        purposes.  In this case, no HTTP request is done, all checks are
        successful.

        Optional is a setting HTTP_BASIC_AUTH_CASE that specifies whether the
        user name will be treated case sensitive or case-insensitive. Any value
        that starts with a 'f' or 'n' will result in a case insensitive
        setting.  The value of HTTP_BASIC_AUTH_CASE is case-insensitive, of
        cuurse.
        """
        user_model = get_user_model()
        if username is None:
            username = kwargs.get(user_model.USERNAME_FIELD)

        url = getattr(settings, 'HTTP_BASIC_AUTH_URL', '')
        if url == '':
            LOGGER.error("No HTTP_BASIC_AUTH_URL")
            return None

        case_spec = getattr(settings, 'HTTP_BASIC_AUTH_CASE', "y").lower()
        if case_spec[:1] in ("f", "n"):
            username = username.lower()

        if not self.checkpw_basic_auth(
                settings.HTTP_BASIC_AUTH_URL, username, password):
            return None

        user, _ = user_model.objects.get_or_create(**{
            user_model.USERNAME_FIELD: username,
            })
        return user if self.user_can_authenticate(user) else None
