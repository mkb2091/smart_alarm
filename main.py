import time
import sched
import logging

import flask
import pyttsx3

app = flask.Flask(__name__)
scheduler = sched.scheduler(time.time, time.sleep)

alarms = [{'title':'MyAlarm', 'content':'MyAlarmContent'}]
notifications = [{'title':'MyNotification', 'content':'MyNotificationContent'}]

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    alarm_time = flask.request.args.get('alarm')
    if alarm_time is not None:
        try:
            alarm_time = time.strptime(alarm_time, '%Y-%m-%dT%H:%M')
            name = flask.request.args.get('two')
            include_news = flask.request.args.get('news') is not None
            include_weather = flask.request.args.get('weather') is not None
            alarms.append({'title': name, 'content': ' and '.join(
                (['with news'] if include_news else [])
                + (['with weather'] if include_weather else [])
                )})
            print(f'Registering an alarm: {name} on {alarm_time}, include news: {include_news}, '
                  f'include weather: {include_weather}')
        except ValueError:
            logging.warning('Invalid time format given: %s' % alarm_time)
    return flask.render_template(
        'index.html',
        title='Daily Update',
        image='image.png',
        alarms=alarms,
        notifications=notifications
        )


if __name__ == '__main__':
    app.run()
