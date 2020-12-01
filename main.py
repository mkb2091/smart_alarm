import time
import sched

import flask

app = flask.Flask(__name__)
scheduler = sched.scheduler(time.time, time.sleep)

alarms = []
notifications = []

@app.route('/static/images/')
def images():
    return ''

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    if flask.request.args.get('alarm') is not None:
        alarm_time = flask.request.args.get('alarm')
        name = flask.request.args.get('two')
        include_news = flask.request.args.get('news') is not None
        include_weather = flask.request.args.get('weather') is not None
        print(f'Registering an alarm: {name} on {alarm_time}, include news: {include_news}, '
              f'include weather: {include_weather}')
    return flask.render_template(
        'index.html',
        title='Daily Update',
        alarms=alarms,
        notifications=notifications
        )


if __name__ == '__main__':
    app.run()
