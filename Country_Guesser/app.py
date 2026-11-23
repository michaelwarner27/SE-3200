import flask, flask_cors
import json
import os
import secrets
import functools
import urllib.error
import urllib.parse
import urllib.request
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from server.database import Database

load_dotenv()  # reads RESTCOUNTRIES_KEY from a git-ignored .env file

app = flask.Flask(__name__)
flask_cors.CORS(app)
db = Database()
bcrypt = Bcrypt(app)
sessions = {}

COUNTRY_FIELDS = ["common_name", "official_name", "population", "html_flag_code", "area"]
INT_FIELDS = ("population", "area")
COUNTRY_API_URL = "https://api.restcountries.com/countries/v5/names.common/"
country_cache = {}  # common name -> restcountries JSON, so repeat lookups don't use up API quota
USER_FIELDS = ["first_name", "last_name", "email", "password"]
LOGIN_FIELDS = ["email", "password"]


class ApiError(Exception):
    """Raise this anywhere in a route; handle_api_error turns it into a JSON response."""
    def __init__(self, message, status):
        super().__init__(message)
        self.message = message
        self.status = status


def error(message, status):
    return flask.jsonify({"error": message}), status


def require_auth(handler):
    @functools.wraps(handler)
    def wrapper(*args, **kwargs):
        user_id = get_current_user_id()
        if user_id is None:
            raise ApiError("Authentication Required", 401)
        flask.g.user_id = user_id
        return handler(*args, **kwargs)
    return wrapper


def get_current_user_id():
    session = sessions.get(flask.request.cookies.get("session_id"))
    return session["user_id"] if session else None


def parse_body(fields):
    """Return the values in the order of `fields`, or raise ApiError(400)."""
    data = flask.request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ApiError("Request body must be a JSON object", 400)
    missing = [f for f in fields if data.get(f) in (None, "")]
    if missing:
        raise ApiError("Missing fields: " + ", ".join(missing), 400)
    values = []
    for f in fields:
        v = data[f]
        if f in INT_FIELDS:
            if isinstance(v, bool) or not isinstance(v, int):
                raise ApiError(f"{f} must be an integer", 400)
        elif not isinstance(v, str):
            raise ApiError(f"{f} must be a string", 400)
        values.append(v)
    return values


@app.route("/", methods=["GET"])
def render_home():
    return flask.render_template("index.html")


@app.route("/countries", methods=["GET"])
@require_auth
def handle_list():
    return flask.jsonify(db.get_all_countries(flask.g.user_id)), 200


@app.route("/countries/<int:id>", methods=["GET"])
@require_auth
def handle_retrieve(id):
    country = db.get_country(id, flask.g.user_id)
    if country is None:
        raise ApiError("Country not found", 404)
    return flask.jsonify(country), 200


@app.route("/countries", methods=["POST"])
@require_auth
def handle_create():
    values = parse_body(COUNTRY_FIELDS)
    return flask.jsonify(db.create_country(*values, user_id=flask.g.user_id)), 201


@app.route("/countries/<int:id>", methods=["PUT"])
@require_auth
def handle_replace(id):
    values = parse_body(COUNTRY_FIELDS)
    country = db.update_country(id, *values, user_id=flask.g.user_id)
    if country is None:
        raise ApiError("Country not found", 404)
    return flask.jsonify(country), 200


@app.route("/countries/<int:id>", methods=["DELETE"])
@require_auth
def handle_delete(id):
    if not db.delete_country(id, flask.g.user_id):
        raise ApiError("Country not found", 404)
    return flask.jsonify({"message": "Country deleted"}), 200


@app.route("/api/country/<path:name>", methods=["GET"])
@require_auth
def handle_country_info(name):
    """Proxy to restcountries.com so the API key stays on the server."""
    key = name.strip().lower()
    if key in country_cache:
        return flask.jsonify(country_cache[key]), 200

    api_key = os.environ.get("RESTCOUNTRIES_KEY")
    if not api_key:
        raise ApiError("Server is missing RESTCOUNTRIES_KEY", 500)

    request = urllib.request.Request(
        COUNTRY_API_URL + urllib.parse.quote(name.strip(), safe=""),
        headers={"Authorization": f"Bearer {api_key}", "User-Agent": "country-guesser"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.load(response)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise ApiError("Country not found", 404)
        raise ApiError("Country service error", 502)
    except (urllib.error.URLError, TimeoutError, ValueError):
        raise ApiError("Country service unavailable", 502)

    if not data.get("data", {}).get("objects"):
        raise ApiError("Country not found", 404)
    country_cache[key] = data
    return flask.jsonify(data), 200


@app.route("/users", methods=["POST"])
def handle_create_user():
    first, last, email, pw = parse_body(USER_FIELDS)

    email = str(email).strip().lower()
    name, at, domain = email.partition("@")
    if not name or not at or "." not in domain or " " in email:
        raise ApiError("Please enter a valid email address", 400)

    if not 8 <= len(pw) <= 72:
        raise ApiError("Password must be between 8 and 72 characters", 400)

    pw_hash = bcrypt.generate_password_hash(pw).decode()
    user = db.create_user(first, last, email, pw_hash)
    if user is None:
        raise ApiError("An account with that email already exists", 409)
    return flask.jsonify(user), 201


@app.route("/sessions", methods=["POST"])
def handle_create_session():
    email, pw = parse_body(LOGIN_FIELDS)
    user = db.get_user_by_email(str(email).strip().lower())
    if not user or not bcrypt.check_password_hash(user["password_hash"], pw):
        raise ApiError("Unknown username or password", 401)

    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = {"user_id": user["id"]}

    response = flask.jsonify({
        "id": user["id"], "first_name": user["first_name"], "last_name": user["last_name"], "email": user["email"],
    })
    response.set_cookie("session_id", session_id, httponly=True, samesite="Lax")
    return response, 200


@app.route("/sessions/current", methods=["GET"])
def handle_get_session():
    user_id = get_current_user_id()
    if user_id is None:
        raise ApiError("Not authenticated", 401)
    return flask.jsonify(db.get_user(user_id)), 200


@app.route("/sessions", methods=["DELETE"])
def handle_delete_session():
    sessions.pop(flask.request.cookies.get("session_id"), None)
    response = flask.jsonify({"message": "Logged out"})
    response.delete_cookie("session_id")
    return response, 200


# ---- Error handlers ----

@app.errorhandler(ApiError)
def handle_api_error(e):
    # Every error raised by our own routes (400, 401, 404, 409, ...) ends up here.
    return error(e.message, e.status)


@app.errorhandler(404)
def handle_404(e):
    # Unknown URLs (Flask raises this itself)
    return error("Not Found", 404)


@app.errorhandler(405)
def handle_405(e):
    # Known URL, wrong HTTP method (Flask raises this itself)
    return error("Method Not Allowed", 405)


@app.errorhandler(500)
def handle_500(e):
    # Any unexpected crash
    return error("Internal Server Error", 500)


if __name__ == "__main__":
    app.run(debug=True, port=5500)
