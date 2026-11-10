import flask, flask_cors
from server.database import Database

app = flask.Flask(__name__)
flask_cors.CORS(app)
db = Database()

FIELDS = ["common_name", "official_name", "population", "html_flag_code", "area"]
INT_FIELDS = ("population", "area")


def error(message, status):
    return flask.jsonify({"error": message}), status


def parse_body():
    """Return (values, error_response). values is a list in FIELDS order."""
    data = flask.request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, error("Request body must be a JSON object", 400)
    missing = [f for f in FIELDS if data.get(f) in (None, "")]
    if missing:
        return None, error("Missing fields: " + ", ".join(missing), 400)
    values = []
    for f in FIELDS:
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
    values, err = parse_body()
    if err:
        return err
    return flask.jsonify(db.create_country(*values)), 201


@app.route("/countries/<int:id>", methods=["PUT"])
def handle_replace(id):
    values, err = parse_body()
    if err:
        return err
    country = db.update_country(id, *values)
    if country is None:
        return error("Country not found", 404)
    return flask.jsonify(country), 200


@app.route("/countries/<int:id>", methods=["DELETE"])
def handle_delete(id):
    if not db.delete_country(id):
        return error("Country not found", 404)
    return flask.jsonify({"message": "Country deleted"}), 200


@app.errorhandler(404)
def handle_404(e):
    return error("Not Found", 404)


@app.errorhandler(405)
def handle_405(e):
    return error("Method Not Allowed", 405)


@app.errorhandler(500)
def handle_500(e):
    return error("Internal Server Error", 500)


if __name__ == "__main__":
    app.run(debug=True, port=5500)
