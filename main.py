import logging
import sched
import time
import re

import uk_covid19
import pyttsx3
import flask

app = flask.Flask(__name__)
scheduler = sched.scheduler(time.time, time.sleep)

alarms = []
notifications = [{'title':'MyNotification', 'content':'MyNotificationContent'}]

def handle_alarm():
    '''
    Handles what happens when an alarm is triggered. Should be called by the scheduler
    '''
    try:
        alarm = alarms.pop(0)
        try:
            assert alarm['time'] <= time.gmtime()
            # Check that it is actually an event in the past
            # Assert is used for the check so that it can be disabled by calling python3 -OO
        except AssertionError:
            logging.warning('handle_alarm called when alarm is in the future. Alarm time: %s, current time: %s' % (alarm['time'], time.gmtime()))
        print(alarm)
    except IndexError:
        logging.warning('Called handle_alarm with an empty alarm list')


def register_alarm(alarm_time, name: str, include_news: bool, include_weather: bool, log: bool=True):
    '''
    Creates the alarm
    '''
    alarm_time_str = time.strftime('%Y-%m-%d %H:%M', alarm_time)
    alarm = {
        'title': name,
        'content': 'Alarm on %s %s'  % (
            alarm_time_str,
            ' and '.join(
                (['with news'] if include_news else [])
                + (['with weather'] if include_weather else [])
                )
            ),
        'time': alarm_time}
    if alarm not in alarms:
        alarms.append(alarm)
        alarms.sort(key=lambda a: a['time'])
        # Would me more efficient to insert alarm in correct position,
        # but it is easier to append and then sort
        scheduler.enterabs(time.mktime(alarm_time), 1, handle_alarm)
        if log:
            logging.info(f'Registering an alarm: {name} on {alarm_time_str}, include news: {include_news}, '
                  f'include weather: {include_weather}')

def cancel_alarm(alarm_name: str, log=True):
    '''
    Removes the alarm of the specified name
    '''
    location = None
    for (i, alarm) in enumerate(alarms):
        if alarm['title'] == alarm_name:
            location = i
            break
    if location is not None:
        del alarms[i]
        if log:
            logging.info(f'Canceling an alarm: {alarm_name}')
    else:
        logging.warning(f'Attempted to cancel an alarm that does not exist: {alarm_name}')

def add_alarm_parser():
    '''
    Checks if the current request is a alarm creation request, and if it is, creates the alarm
    '''
    alarm_time = flask.request.args.get('alarm')
    if alarm_time is not None:
        try:
            alarm_time = time.strptime(alarm_time, '%Y-%m-%dT%H:%M')
            alarm_name = flask.request.args.get('two')
            include_news = flask.request.args.get('news') is not None
            include_weather = flask.request.args.get('weather') is not None

            register_alarm(alarm_time, alarm_name, include_news, include_weather)
        except ValueError:
            logging.warning('Invalid time format given: %s' % alarm_time)

def cancel_alarm_parser():
    '''
    Checks if the current request is a cancel alarm request, and if it is, it cancels the alarm
    '''
    alarm_name = flask.request.args.get('alarm_item')
    if alarm_name is not None:
        cancel_alarm(alarm_name)

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    add_alarm_parser()
    cancel_alarm_parser()
    scheduler.run(False)
    return flask.render_template(
        'index.html',
        title='Daily Update',
        image='image.png',
        alarms=alarms,
        notifications=notifications
        )


if __name__ == '__main__':
    try:
        with open('log.log') as file:
            for line in file:
                register_match = re.match(
                    r'INFO:\w+:Registering an alarm: (.+) on (.+), '
                    r'include news: ((?:True)|(?:False)), include '
                    r'weather: ((?:True)|(?:False))',
                    line
                    )
                if register_match:
                    alarm_name, alarm_time, include_news, include_weather = register_match.groups()
                    alarm_time = time.strptime(alarm_time, '%Y-%m-%d %H:%M')
                    include_news = include_news == 'True'
                    include_weather = include_weather == 'True'
                    if alarm_time > time.gmtime():
                        register_alarm(alarm_time, alarm_name, include_news, include_weather, log=False)
                cancel_match = re.match(
                    r'INFO:\w+:Canceling an alarm: (\w+)',
                    line
                    )
                if cancel_match:
                    cancel_alarm(cancel_match.group(1), log=False)
    except Exception as error:
        print(error)
    logging.basicConfig(filename='log.log', encoding='utf-8', level=logging.DEBUG)
    app.run()
