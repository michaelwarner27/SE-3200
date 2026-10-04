import flask
app = flask.Flask(__name__)

users = {
    '':'',
    'Michael' : 'password'
}
@app.route('/')
def view_form():
    return flask.render_template('login.html')

@app.route('/handle_get', methods=['GET'])
def handle_get():
    if flask.request.method =='GET':
        username = flask.request.args['username']
        password = flask.request.args['password']
        if username in users and password == users[username]:
            print("Success")
            return flask.render_template('index.html')
            # return '<h1>Welcome!</h1>'
        else:
            return '<h1>Invalid credentials!</h1>'
            # return flask.render_template('login.html')
    else:
        return flask.render_template('login.html')

@app.route('/handle_post', methods=['POST'])
def handle_post():
    if flask.request.method == 'POST':
        username = flask.request.form['username']
        password = flask.request.form['password']
        if username in users and password == users[username]:
            print("Success")
            return flask.render_template('index.html')
            # return '<h1>Welcome!</h1>'
        else:
            return '<h1>Invalid credentials!</h1>'
            # return flask.render_template('login.html')
    else:
        return flask.render_template('login.html')
    
if __name__ == '__main__':
    app.run()