import flask, flask_cors
import secrets
from flask_bcrypt import Bcrypt
from server.database import Database

app = flask.Flask(__name__)
flask_cors.CORS(app)
db = Database()
bcrypt = Bcrypt(app)
sessions = {}

COUNTRY_FIELDS = ["common_name", "official_name", "population", "html_flag_code", "area"]
INT_FIELDS = ("population", "area")
USER_FIELDS = ["first_name", "last_name", "email", "password"]
LOGIN_FIELDS = ["email", "password"]

def error(message, status):
    return flask.jsonify({"error": message}), status


def parse_body(fields):
    """Return (values, error_response). values is a list in FIELDS order."""
    data = flask.request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, error("Request body must be a JSON object", 400)
    missing = [f for f in fields if data.get(f) in (None, "")]
    if missing:
        return None, error("Missing fields: " + ", ".join(missing), 400)
    values = []
    for f in fields:
        v = data[f]
        if f in INT_FIELDS:
            if isinstance(v, bool) or not isinstance(v, int):
                return None, error(f"{f} must be an integer", 400)
        elif not isinstance(v, str):
            return None, error(f"{f} must be a string", 400)
        values.append(v)
    return values, None


@app.route("/", methods=["GET"])
def render_home():
    return flask.render_template("index.html")


@app.route("/countries", methods=["GET"])
def handle_list():
    return flask.jsonify(db.get_all_countries()), 200


@app.route("/countries/<int:id>", methods=["GET"])
def handle_retrieve(id):
    country = db.get_country(id)
    if country is None:
        return error("Country not found", 404)
    return flask.jsonify(country), 200


@app.route("/countries", methods=["POST"])
def handle_create():
    values, err = parse_body(COUNTRY_FIELDS)
    if err:
        return err
    if not values:
        return error("Parse fail", 404)
    return flask.jsonify(db.create_country(*values)), 201


@app.route("/countries/<int:id>", methods=["PUT"])
def handle_replace(id):
    values, err = parse_body(COUNTRY_FIELDS)
    if err:
        return err
    if not values:
        return error("Parse fail", 404)
    country = db.update_country(id, *values)
    if country is None:
        return error("Country not found", 404)
    return flask.jsonify(country), 200


@app.route("/countries/<int:id>", methods=["DELETE"])
def handle_delete(id):
    if not db.delete_country(id):
        return error("Country not found", 404)
    return flask.jsonify({"message": "Country deleted"}), 200

@app.route("/users", methods=["POST"])
def handle_create_user():
    values, err = parse_body(USER_FIELDS)
    if err:
        return err
    if not values:
        return error("Parse fail", 404)
    first, last, email, pw = values
    #TODO if email bad reject
    str(email).strip().lower()
    pw_hash = bcrypt.generate_password_hash(pw).decode()
    user = db.create_user(first, last, email, pw_hash)
    if user is None:
        return error("An account with that email already exists", 409)
    return flask.jsonify(user), 201


@app.route("/sessions", methods=["POST"])
def handle_create_session():
    values, err = parse_body(LOGIN_FIELDS)
    if err:
        return err
    if not values:
        return error("Parse fail", 404)
    email, pw = values
    user = db.get_user_by_email(str(email).strip().lower())
    if not user or not bcrypt.check_password_hash(user["password_hash"], pw):
        return error("Unknown username or password", 401)

    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = {"user_id": user["id"]}

    response = flask.jsonify({
        "id":user["id"], "first_name":user["first_name"], "last_name":user["last_name"], "email":user["email"],
    })
    response.set_cookie("session_id", session_id, httponly=True, samesite="Lax")
    return response, 200

@app.route("/sessions/current", methods=["GET"])
def handle_get_session():
    user_id = get_current_user_id()
    if user_id is None:
        return error("Not authenticated", 401)
    return flask.jsonify(db.get_user(user_id)), 200

@app.route("/sessions", methods=["DELETE"])
def handle_delete_session():
    sessions.pop(flask.request.cookies.get("session_id"), None)
    response = flask.jsonify({"message": "Logged out"})
    response.delete_cookie("session_id")
    return response, 200

@app.errorhandler(404)
def handle_404(e):
    return error("Not Found", 404)


@app.errorhandler(405)
def handle_405(e):
    return error("Method Not Allowed", 405)


@app.errorhandler(500)
def handle_500(e):
    return error("Internal Server Error", 500)

def get_current_user_id():
    session = sessions.get(flask.request.cookies.get("session_id"))
    return session["user_id"] if session else None



if __name__ == "__main__":
    app.run(debug=True, port=5500)
