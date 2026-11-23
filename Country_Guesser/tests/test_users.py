"""Tests for registration, login, sessions and countries authorization.

Run from the project root:
    python -m unittest discover tests
"""
import os
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.database import Database

# app.py creates `db = Database()` at import time. Point that default at a throwaway file first
# so importing app never touches the real server/countries.db.
_IMPORT_DIR = tempfile.mkdtemp()
Database.__init__.__defaults__ = (os.path.join(_IMPORT_DIR, "import.db"),)

import app as app_module  # noqa: E402


ADA = {"first_name": "Ada", "last_name": "Lovelace", "email": "ada@example.com", "password": "correcthorse"}
BOB = {"first_name": "Bob", "last_name": "Barker", "email": "bob@example.com", "password": "batterystaple"}
DENMARK = {
    "common_name": "Denmark",
    "official_name": "Kingdom of Denmark",
    "population": 6000000,
    "html_flag_code": "&#127465;&#127472;",
    "area": 16000,
}
NORWAY = {
    "common_name": "Norway",
    "official_name": "Kingdom of Norway",
    "population": 5000000,
    "html_flag_code": "&#127475;&#127476;",
    "area": 125000,
}


class AppTestCase(unittest.TestCase):
    """Gives every test a fresh temp database, an empty session store and clean clients."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp.name, "test.db")
        app_module.db = Database(self.db_path)
        app_module.sessions.clear()
        app_module.app.testing = True
        self.client = app_module.app.test_client()      # one browser
        self.other = app_module.app.test_client()       # a second browser (separate cookies)

    def tearDown(self):
        self.tmp.cleanup()

    # --- helpers ---
    def register(self, user=ADA, client=None):
        return (client or self.client).post("/users", json=user)

    def login(self, user=ADA, client=None):
        return (client or self.client).post(
            "/sessions", json={"email": user["email"], "password": user["password"]}
        )

    def register_and_login(self, user=ADA, client=None):
        self.assertEqual(self.register(user, client).status_code, 201)
        self.assertEqual(self.login(user, client).status_code, 200)

    def stored_user(self, email):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        finally:
            conn.close()


class RegistrationTests(AppTestCase):
    def test_register_success(self):
        res = self.register()
        self.assertEqual(res.status_code, 201)
        body = res.get_json()
        self.assertEqual(body["email"], "ada@example.com")
        self.assertEqual(body["first_name"], "Ada")
        self.assertEqual(body["last_name"], "Lovelace")
        self.assertIn("id", body)

    def test_response_never_contains_password_or_hash(self):
        body = self.register().get_json()
        self.assertNotIn("password", body)
        self.assertNotIn("password_hash", body)
        self.assertNotIn("correcthorse", str(body))

    def test_password_is_stored_as_bcrypt_hash(self):
        self.register()
        row = self.stored_user("ada@example.com")
        self.assertNotEqual(row["password_hash"], ADA["password"])
        self.assertNotIn(ADA["password"], row["password_hash"])
        self.assertTrue(row["password_hash"].startswith("$2b$"))

    def test_same_password_gets_different_hashes(self):
        self.register(ADA)
        self.register({**BOB, "password": ADA["password"]})
        self.assertNotEqual(
            self.stored_user("ada@example.com")["password_hash"],
            self.stored_user("bob@example.com")["password_hash"],
        )

    def test_duplicate_email_is_409(self):
        self.register()
        res = self.register()
        self.assertEqual(res.status_code, 409)
        self.assertIn("error", res.get_json())

    def test_duplicate_email_ignores_case_and_whitespace(self):
        self.register()
        res = self.register({**BOB, "email": "  ADA@Example.COM "})
        self.assertEqual(res.status_code, 409)

    def test_email_is_trimmed_and_lowercased(self):
        res = self.register({**ADA, "email": "  Ada@Example.COM "})
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.get_json()["email"], "ada@example.com")
        self.assertEqual(self.login().status_code, 200)

    def test_missing_field_is_400(self):
        for field in ("first_name", "last_name", "email", "password"):
            with self.subTest(missing=field):
                payload = {k: v for k, v in ADA.items() if k != field}
                res = self.register(payload)
                self.assertEqual(res.status_code, 400)
                self.assertIn(field, res.get_json()["error"])

    def test_empty_field_is_400(self):
        self.assertEqual(self.register({**ADA, "first_name": ""}).status_code, 400)

    def test_wrong_field_type_is_400(self):
        self.assertEqual(self.register({**ADA, "first_name": 123}).status_code, 400)

    def test_body_must_be_json_object(self):
        self.assertEqual(self.client.post("/users", data="hello").status_code, 400)
        self.assertEqual(self.client.post("/users", json=["a", "b"]).status_code, 400)

    def test_invalid_emails_are_400(self):
        for bad in ("not-an-email", "@example.com", "ada@", "ada@example", "a da@example.com"):
            with self.subTest(email=bad):
                res = self.register({**ADA, "email": bad})
                self.assertEqual(res.status_code, 400)
                self.assertIn("email", res.get_json()["error"].lower())
        self.assertIsNone(self.stored_user("not-an-email"))

    def test_password_length_limits(self):
        cases = [("a" * 7, 400), ("a" * 8, 201), ("a" * 72, 201), ("a" * 73, 400), ("a" * 500, 400)]
        for i, (password, expected) in enumerate(cases):
            with self.subTest(length=len(password)):
                res = self.register({**ADA, "email": f"user{i}@example.com", "password": password})
                self.assertEqual(res.status_code, expected)
                if expected == 400:
                    self.assertIn("password", res.get_json()["error"].lower())

    def test_rejected_registration_creates_no_user(self):
        self.register({**ADA, "password": "short"})
        self.assertIsNone(self.stored_user("ada@example.com"))


class LoginTests(AppTestCase):
    def setUp(self):
        super().setUp()
        self.assertEqual(self.register().status_code, 201)

    def test_login_success_returns_basic_user_data(self):
        res = self.login()
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertEqual(body["email"], "ada@example.com")
        self.assertEqual(body["first_name"], "Ada")
        self.assertEqual(body["last_name"], "Lovelace")
        self.assertIn("id", body)
        self.assertNotIn("password_hash", body)
        self.assertNotIn("password", body)

    def test_login_sets_httponly_session_cookie(self):
        cookies = self.login().headers.get_all("Set-Cookie")
        session = [c for c in cookies if c.startswith("session_id=")]
        self.assertEqual(len(session), 1)
        self.assertIn("HttpOnly", session[0])
        self.assertIn("SameSite=Lax", session[0])

    def test_wrong_password_is_401_and_sets_no_cookie(self):
        res = self.client.post("/sessions", json={"email": ADA["email"], "password": "wrongpassword"})
        self.assertEqual(res.status_code, 401)
        self.assertEqual(res.headers.get_all("Set-Cookie"), [])

    def test_unknown_email_is_401(self):
        res = self.client.post("/sessions", json={"email": "nobody@example.com", "password": "correcthorse"})
        self.assertEqual(res.status_code, 401)

    def test_wrong_password_and_unknown_email_give_same_message(self):
        wrong_pw = self.client.post("/sessions", json={"email": ADA["email"], "password": "wrongpassword"})
        no_user = self.client.post("/sessions", json={"email": "nobody@example.com", "password": "wrongpassword"})
        self.assertEqual(wrong_pw.get_json(), no_user.get_json())

    def test_missing_fields_are_400(self):
        self.assertEqual(self.client.post("/sessions", json={"email": ADA["email"]}).status_code, 400)
        self.assertEqual(self.client.post("/sessions", json={"password": "correcthorse"}).status_code, 400)
        self.assertEqual(self.client.post("/sessions", data="hello").status_code, 400)

    def test_login_ignores_email_case_and_whitespace(self):
        res = self.client.post("/sessions", json={"email": " ADA@Example.com ", "password": ADA["password"]})
        self.assertEqual(res.status_code, 200)

    def test_password_is_case_sensitive(self):
        res = self.client.post("/sessions", json={"email": ADA["email"], "password": "CORRECTHORSE"})
        self.assertEqual(res.status_code, 401)

    def test_each_login_gets_a_new_session_id(self):
        self.login()
        self.login(client=self.other)
        self.assertEqual(len(app_module.sessions), 2)


class SessionTests(AppTestCase):
    def test_current_without_cookie_is_401(self):
        self.assertEqual(self.client.get("/sessions/current").status_code, 401)

    def test_current_after_login_returns_user(self):
        self.register_and_login()
        res = self.client.get("/sessions/current")
        self.assertEqual(res.status_code, 200)
        body = res.get_json()
        self.assertEqual(body["email"], "ada@example.com")
        self.assertNotIn("password_hash", body)

    def test_forged_session_cookie_is_401(self):
        self.client.set_cookie("session_id", "forged-session-id")
        self.assertEqual(self.client.get("/sessions/current").status_code, 401)

    def test_session_store_only_holds_user_id(self):
        self.register_and_login()
        self.assertEqual(len(app_module.sessions), 1)
        (data,) = app_module.sessions.values()
        self.assertEqual(list(data.keys()), ["user_id"])

    def test_sessions_are_independent_per_browser(self):
        self.register_and_login(ADA, self.client)
        self.assertEqual(self.other.get("/sessions/current").status_code, 401)

    def test_logout_ends_session(self):
        self.register_and_login()
        res = self.client.delete("/sessions")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.client.get("/sessions/current").status_code, 401)
        self.assertEqual(app_module.sessions, {})

    def test_old_session_id_is_dead_after_logout(self):
        self.register_and_login()
        old_id = self.client.get_cookie("session_id").value
        self.client.delete("/sessions")
        self.client.set_cookie("session_id", old_id)
        self.assertEqual(self.client.get("/countries").status_code, 401)

    def test_logout_without_session_is_harmless(self):
        self.assertEqual(self.client.delete("/sessions").status_code, 200)

    def test_logout_only_affects_own_session(self):
        self.register_and_login(ADA, self.client)
        self.register_and_login(BOB, self.other)
        self.client.delete("/sessions")
        self.assertEqual(self.other.get("/sessions/current").status_code, 200)


class CountriesAuthTests(AppTestCase):
    def test_every_countries_route_requires_login(self):
        calls = [
            ("get", "/countries", None),
            ("get", "/countries/1", None),
            ("post", "/countries", DENMARK),
            ("put", "/countries/1", DENMARK),
            ("delete", "/countries/1", None),
        ]
        for method, url, payload in calls:
            with self.subTest(route=f"{method.upper()} {url}"):
                kwargs = {"json": payload} if payload else {}
                res = getattr(self.client, method)(url, **kwargs)
                self.assertEqual(res.status_code, 401)
                self.assertIn("error", res.get_json())

    def test_forged_cookie_cannot_access_countries(self):
        self.client.set_cookie("session_id", "forged-session-id")
        self.assertEqual(self.client.get("/countries").status_code, 401)

    def test_home_page_is_public(self):
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_logged_in_user_starts_with_empty_list(self):
        self.register_and_login()
        res = self.client.get("/countries")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json(), [])

    def test_create_returns_row_owned_by_current_user(self):
        self.register_and_login()
        user_id = self.client.get("/sessions/current").get_json()["id"]
        res = self.client.post("/countries", json=DENMARK)
        self.assertEqual(res.status_code, 201)
        body = res.get_json()
        self.assertIsNotNone(body)
        self.assertEqual(body["common_name"], "Denmark")
        self.assertEqual(body["user_id"], user_id)

    def test_user_id_in_body_is_ignored(self):
        self.register_and_login(ADA, self.client)
        self.register_and_login(BOB, self.other)
        ada_id = self.client.get("/sessions/current").get_json()["id"]
        bob_id = self.other.get("/sessions/current").get_json()["id"]
        res = self.other.post("/countries", json={**NORWAY, "user_id": ada_id})
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.get_json()["user_id"], bob_id)
        self.assertEqual(self.client.get("/countries").get_json(), [])

    def test_create_validation_errors_are_400(self):
        self.register_and_login()
        self.assertEqual(self.client.post("/countries", json={**DENMARK, "population": "lots"}).status_code, 400)
        self.assertEqual(self.client.post("/countries", json={"common_name": "X"}).status_code, 400)
        self.assertEqual(self.client.post("/countries", data="hello").status_code, 400)

    def test_full_crud_on_own_rows(self):
        self.register_and_login()
        row_id = self.client.post("/countries", json=DENMARK).get_json()["id"]

        res = self.client.get(f"/countries/{row_id}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["common_name"], "Denmark")
        self.assertEqual(len(self.client.get("/countries").get_json()), 1)

        res = self.client.put(f"/countries/{row_id}", json={**DENMARK, "official_name": "Updated"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["official_name"], "Updated")

        self.assertEqual(self.client.delete(f"/countries/{row_id}").status_code, 200)
        self.assertEqual(self.client.get(f"/countries/{row_id}").status_code, 404)
        self.assertEqual(self.client.get("/countries").get_json(), [])

    def test_missing_row_is_404(self):
        self.register_and_login()
        self.assertEqual(self.client.get("/countries/999").status_code, 404)
        self.assertEqual(self.client.put("/countries/999", json=DENMARK).status_code, 404)
        self.assertEqual(self.client.delete("/countries/999").status_code, 404)

    def test_users_only_see_their_own_countries(self):
        self.register_and_login(ADA, self.client)
        self.register_and_login(BOB, self.other)
        self.client.post("/countries", json=DENMARK)
        self.other.post("/countries", json=NORWAY)

        ada_rows = self.client.get("/countries").get_json()
        bob_rows = self.other.get("/countries").get_json()
        self.assertEqual([r["common_name"] for r in ada_rows], ["Denmark"])
        self.assertEqual([r["common_name"] for r in bob_rows], ["Norway"])

    def test_user_cannot_read_update_or_delete_another_users_row(self):
        self.register_and_login(ADA, self.client)
        self.register_and_login(BOB, self.other)
        row_id = self.client.post("/countries", json=DENMARK).get_json()["id"]

        self.assertEqual(self.other.get(f"/countries/{row_id}").status_code, 404)
        self.assertEqual(self.other.put(f"/countries/{row_id}", json=NORWAY).status_code, 404)
        self.assertEqual(self.other.delete(f"/countries/{row_id}").status_code, 404)

        # Ada's row is untouched
        row = self.client.get(f"/countries/{row_id}").get_json()
        self.assertEqual(row["common_name"], "Denmark")
        self.assertEqual(row["official_name"], "Kingdom of Denmark")

    def test_access_is_lost_after_logout(self):
        self.register_and_login()
        self.client.post("/countries", json=DENMARK)
        self.client.delete("/sessions")
        self.assertEqual(self.client.get("/countries").status_code, 401)

    def test_data_survives_logging_back_in(self):
        self.register_and_login()
        self.client.post("/countries", json=DENMARK)
        self.client.delete("/sessions")
        self.assertEqual(self.login().status_code, 200)
        self.assertEqual(len(self.client.get("/countries").get_json()), 1)


class ErrorHandlerTests(AppTestCase):
    def test_unknown_route_returns_json_404(self):
        res = self.client.get("/nope")
        self.assertEqual(res.status_code, 404)
        self.assertEqual(res.get_json(), {"error": "Not Found"})

    def test_wrong_method_returns_json_405(self):
        res = self.client.patch("/users")
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.get_json(), {"error": "Method Not Allowed"})

    def test_api_errors_are_json_with_error_key(self):
        res = self.register({**ADA, "email": "bad"})
        self.assertEqual(res.status_code, 400)
        self.assertTrue(res.is_json)
        self.assertEqual(list(res.get_json().keys()), ["error"])


if __name__ == "__main__":
    unittest.main()
