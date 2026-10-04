import flask, flask_cors
app = flask.Flask(__name__)
flask_cors.CORS(app)

@app.route("/", methods=["GET"])
def render_home():
    return flask.render_template('index.html')

#POST 
@app.route('/messages', methods=['POST'])
def handle_post(): 
    if flask.request.method == 'POST':
        message = flask.request.form['message']
        if not message:
            return '', 400
        with open("message.txt", "a") as file:
            file.write(message + "\n")
        return '', 201
    else:
        return '', 400
#GET
@app.route('/messages', methods=['GET']) 
def handle_get():
    json = ''
    if flask.request.method == 'GET':
        lines = []
        with open("message.txt", "r") as file:
            for line in file:
                lines.append(line)
        if lines:
            return flask.jsonify(lines)
    return flask.jsonify([]), 200


@app.errorhandler(404)
def error(e):
    return '<h1>Not Found</h1>', 404