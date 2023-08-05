# coding: utf-8
# Flask
from flask import render_template, Blueprint, request, jsonify, current_app, abort
from flask_security import login_required

# Cache
from ..extensions import cache

# Database
from ..models import (Settings,
                      Events,
                      User,
                      Reader)
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy import and_, or_, asc

# System
from datetime import datetime, timedelta


bp = Blueprint('logs', __name__)


@cache.cached(timeout=120, key_prefix='get_preserved_time')
def _get_preserved_time():
    """Gets the amount of time stored in the database

    :returns int months: Number of months stored. This can be from 1 to 4 months of events.
    """
    months = Settings.query.filter(Settings.settings_name == 'MONTHS_PRESERVED')\
        .with_entities(Settings.settings_value).one_or_none()

    if months is None:
        return 4
    else:
        return int(months.settings_value)


@bp.route('/logs/events/<int:user_id>', methods=['GET'])
@login_required
def get_events(user_id):
    """Get all events for user/users

    :param int user_id: User ID number
    :returns json events: Events for selected user
    """
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    event = request.args.get('event_type')

    if (start_time is None) or (end_time is None) or (event is None):
        abort(400)

    def _validate_date(date_text):
        result = True

        try:
            datetime.strptime(date_text, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            result = False

        return result

    start_time = (datetime.now() - timedelta(weeks=16)).strftime('%Y-%m-%d %H:%M:%S') if _validate_date(start_time) is False else start_time
    end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') if _validate_date(end_time) is False else end_time

    filters = [Events.event_time > start_time, Events.event_time < end_time]

    if event is 'D':
        filters.append(Events.event_type == 'DENIED')
    elif event is 'B':
        filters.append(or_(Events.event_type == 'ACCESS', Events.event_type == 'DENIED'))
    else:
        filters.append(Events.event_type == 'ACCESS')

    if user_id != 0:
        filters.append(User.id == user_id)

    usr_events = Events.query \
        .with_entities(Events.id_event,
                       Events.event_time,
                       Events.event_type,
                       User.first_name,
                       User.last_name,
                       Reader.location) \
        .join(User, User.id == Events.user_id) \
        .join(Reader, Reader.idreader == Events.reader_idreader) \
        .filter(and_(*filters)).all()

    if usr_events is not None:
        ret = list()

        for event in usr_events:
            content = event.first_name + ' ' + event.last_name + '<p class="small">(' + str(event.location) + ')</p>'
            val = {
                'id': event.id_event,
                'start': str(event.event_time),
                'content': content,
                'className': 'access' if event.event_type is 'ACCESS' else 'denied',
                'title': event.first_name + ' ' + event.last_name[0] + '. @ ' + str(event.event_time).split(' ')[1]
            }
            ret.append(val)

        return jsonify(ret), 200
    else:
        return jsonify([]), 200


@bp.route('/logs', methods=['GET'])
@cache.cached(timeout=120)
@login_required
def logs():
    """Logs and Reporting page

    :returns html_template logs.html:
    """
    users = dict()

    try:
        ret = User.query.with_entities(User.id, User.first_name, User.last_name) \
            .order_by(asc(User.first_name)) \
            .all()
    except (OperationalError, IntegrityError):
        current_app.logger.error('Unable to read from database')
    else:
        for count, user in enumerate(ret):
            users[count] = (user.id, user.first_name + " " + user.last_name)

    preserved = _get_preserved_time()

    return render_template('logs/logs.html', users=users, preserved=preserved), 200
