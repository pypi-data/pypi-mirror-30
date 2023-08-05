# coding: utf-8
"""
Dashboard
---------

Dashboard displays the current overview of system functions and recent events. It is a protected page and only those
with administrative access can view it.


"""
# Flask
from flask import render_template, Blueprint, jsonify, request, current_app
from flask_security import login_required

# Database tables and conversions
from sqlalchemy.exc import OperationalError, InternalError, IntegrityError
from ..models import (Recent24hEvents,
                      Recent24hEventsSchema,
                      Recent24hDeniedCount,
                      Recent24hApprovedCount,
                      Recent24hApprovedHourly,
                      Recent24hDeniedHourly,
                      Reader,
                      DoorStatus)

# Cache
from ..extensions import cache

# Info
from ..utils.system_info import SystemInfo

# System
from datetime import datetime, timedelta
import re
from subprocess import check_output, CalledProcessError


bp = Blueprint('site', __name__)


@cache.cached(timeout=50, key_prefix='get_health')
def _get_reader_count():
    """Gets the current number of connected readers

    :returns int count: Number of readers 0 - 4
    """
    count = Reader.query.filter_by(status='ACTIVE').count()

    return 0 if count is None else count


@cache.cached(timeout=50, key_prefix='get_denied_count')
def _get_denied_count():
    """Gets the number of denied accesses in the last 24 hours

    :returns int denied_count: Count of denied
    """
    denied_count = Recent24hDeniedCount.query.first()

    return denied_count.denied_count if denied_count is not None else 0


@cache.cached(timeout=50, key_prefix='get_valid_count')
def _get_valid_count():
    """Gets the number of approved accesses in the last 24 hours

    :returns int valid_count: Count of approved
    """
    valid_count = Recent24hApprovedCount.query.first()

    return valid_count.approved_count if valid_count is not None else 0


@cache.cached(timeout=50, key_prefix='get_error_count')
def _get_error_count():
    """Gets the current number of errors listed in the system logs

    :returns int errors: Number of errors on system
    """
    try:
        logs = check_output(['journalctl', '-t', 'modis-monitor', '-t', 'modis-admin', '--since',
                             (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')],
                            timeout=25).decode("utf-8")
    except CalledProcessError as e:
        current_app.logger.error(e)
        return 0
    else:
        return len(re.findall('error', logs.lower()))


@cache.cached(timeout=50, key_prefix='get_summary')
def _get_24_hour_summary():
    """Get 24 hour summary for validations and denials

    :return:
    """
    approved = [0] * 24
    denied = [0] * 24

    _approve = Recent24hApprovedHourly.query.first()
    _denied = Recent24hDeniedHourly.query.first()

    if _approve is not None:
        _approve = _approve.__dict__
        for key, value in _approve.items():
            try:
                a_index = int(key[1:])
            except ValueError:
                pass
            else:
                approved[a_index] = int(value)

    if _denied is not None:
        _denied = _denied.__dict__

        for key, value in _denied.items():
            try:
                d_index = int(key[1:])
            except ValueError:
                pass
            else:
                denied[d_index] = int(value)
    hour = (datetime.now() - timedelta(hours=23)).hour
    hourlist = list()

    for i in range(24):
        hourlist.append(hour)
        hour += 1
        if hour > 23:
            hour = 0

    approved = [approved[i] for i in hourlist]
    denied = [denied[i] for i in hourlist]

    return {'approved': approved, 'denied': denied}


@bp.route('/dashdata', methods=['GET'])
@login_required
def get_dash_data():
    sensors = {'door1': False, 'door2': False}

    reading = DoorStatus.query.all()

    if reading is not None:
        for door in reading:
            sensors['door' + door.door_iddoor] = True if door.status == 'ACTIVE' else False

    return jsonify({'success': sensors})


@bp.route('/events', methods=['POST'])
@login_required
def get_recent_events():
    """Pulls all events on the database

    Displays the user, location and type of event that occurred.

    This is rendered by `Datatables <http://www.datatables.net>`_ with a structure like:

    .. tabularcolumns:: |first_name|last_name|event_type|event_time|location_name|location_direction|

    :returns dict records: JSON object of records
    """

    if request.form:
        action = request.form.get('action', None)

        if action is not None:
            if action == 'request':
                try:
                    recent_events = Recent24hEvents.query.all()
                except (OperationalError, InternalError, IntegrityError):
                    return jsonify({'data': ''})
                else:
                    result, errors = Recent24hEventsSchema().dump(recent_events, many=True)

                    if errors:
                        current_app.logger.debug(errors)
                        return jsonify({'error': 'No records'})
                    else:
                        return jsonify({'data': result})

    return jsonify({'error': 'Poorly formed request'})


@bp.route('/')
@login_required
def index():
    """Index page.

    :returns html_template index.html:
    """

    memory = SystemInfo.get_memory()

    data = {
        'attacks': False,
        'door1': True,
        'door2': True,
        'errors': _get_error_count(),
        'reader_count': _get_reader_count(),
        'denied_count': _get_denied_count(),
        'valid_count': _get_valid_count(),
        'system': SystemInfo.get_system_info(),
        'summary': _get_24_hour_summary(),
        'memory_total': memory[0],
        'memory_free': memory[1],
        'memory_usage': memory[2],
        'storage': SystemInfo.get_disks()[0].get('space_used_percent')
    }

    return render_template('index/index.html', **data)
