# -*- coding: utf-8 -*-

"""Test HTTP basic auth method.

:copyright: (c) 2016 by Detlef Stern
:license: Apache 2.0, see LICENSE
"""

from django.test import TestCase, override_settings

from django_auth_http_basic import HttpBasicAuthBackend


class TestBackend(TestCase):
    def setUp(self):
        self.backend = HttpBasicAuthBackend()


class TestPwChecker(TestBackend):
    """Test the checkpw_pasic_auth method."""

    def test_none(self):
        """A None URL results in successful checks."""
        for username in (None, '', 'a', 'admin', 'zombie'):
            for password in (None, '', '1', '12345', '*'):
                self.assertTrue(
                    self.backend.checkpw_basic_auth(None, username, password),
                    "%s / %s" % (username, password))


class TestAuthenticate(TestBackend):
    """Test the authenticate mathod."""

    @override_settings(HTTP_BASIC_AUTH_URL=None)
    def test_simple(self):
        """A None URL results in successful checks."""
        for username in ('a', 'admin', 'zombie'):
            for password in (None, '', '1', '12345', '*'):
                user = self.backend.authenticate(
                    username=username, password=password)
                self.assertEqual(username, user.username)

    @override_settings(HTTP_BASIC_AUTH_URL=None, HTTP_BASIC_AUTH_CASE='n')
    def test_case_insensitive(self):
        """A None URL results in successful checks."""
        for username in ('A', 'ADMIN', 'ZOMbIE'):
            user = self.backend.authenticate(username=username, password="1")
            self.assertEqual(username.lower(), user.username)
