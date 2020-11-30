import flask

app = flask.Flask(__name__)

##TEMPLATE = open('template.html').read()

alarms = []
notifications = []

@app.route('/static/images/')
def images():
    return ''

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    return flask.render_template(
        'index.html',
        title='Daily Update',
        alarms=alarms,
        notifications=notifications
        )


if __name__ == '__main__':
    app.run()
