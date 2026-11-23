"""Tests for the /api/country/<name> proxy that keeps the restcountries API key on the server.

Run from the project root:
    python -m unittest discover tests
"""
import io
import json
import os
import unittest
import urllib.error
from unittest import mock

from test_users import ADA, AppTestCase, app_module

CANADA = {"data": {"objects": [{"names": {"common": "Canada"}, "population": 41798407}], "meta": {"total": 1}}}


def fake_response(payload):
    return io.BytesIO(json.dumps(payload).encode())


class CountryProxyTests(AppTestCase):
    def setUp(self):
        super().setUp()
        app_module.country_cache.clear()
        patcher = mock.patch.dict(os.environ, {"RESTCOUNTRIES_KEY": "test-key"})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_requires_login(self):
        res = self.client.get("/api/country/Canada")
        self.assertEqual(res.status_code, 401)

    def test_returns_upstream_json_and_sends_key_server_side(self):
        self.register_and_login()
        with mock.patch("urllib.request.urlopen", return_value=fake_response(CANADA)) as urlopen:
            res = self.client.get("/api/country/Canada")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json(), CANADA)
        request = urlopen.call_args[0][0]
        self.assertEqual(request.full_url, "https://api.restcountries.com/countries/v5/names.common/Canada")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")

    def test_name_is_url_encoded(self):
        self.register_and_login()
        with mock.patch("urllib.request.urlopen", return_value=fake_response(CANADA)) as urlopen:
            self.client.get("/api/country/Cocos (Keeling) Islands")
        self.assertTrue(urlopen.call_args[0][0].full_url.endswith("/Cocos%20%28Keeling%29%20Islands"))

    def test_second_lookup_is_served_from_cache(self):
        self.register_and_login()
        with mock.patch("urllib.request.urlopen", side_effect=lambda *a, **k: fake_response(CANADA)) as urlopen:
            self.client.get("/api/country/Canada")
            self.client.get("/api/country/canada")
        self.assertEqual(urlopen.call_count, 1)

    def test_unknown_country_returns_404(self):
        self.register_and_login()
        empty = {"data": {"objects": [], "meta": {"total": 0}}}
        with mock.patch("urllib.request.urlopen", return_value=fake_response(empty)):
            res = self.client.get("/api/country/Atlantis")
        self.assertEqual(res.status_code, 404)
        self.assertEqual(list(res.get_json().keys()), ["error"])

    def test_upstream_failure_returns_502(self):
        self.register_and_login()
        boom = urllib.error.HTTPError("url", 429, "Too Many Requests", {}, None)
        with mock.patch("urllib.request.urlopen", side_effect=boom):
            res = self.client.get("/api/country/Canada")
        self.assertEqual(res.status_code, 502)

    def test_missing_key_returns_500(self):
        self.register_and_login()
        with mock.patch.dict(os.environ, {}, clear=True):
            res = self.client.get("/api/country/Canada")
        self.assertEqual(res.status_code, 500)


if __name__ == "__main__":
    unittest.main()
