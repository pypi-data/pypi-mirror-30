# coding: utf-8

# OS
from collections import defaultdict
import os
import re
from datetime import datetime

# Flask
from flask import render_template, Blueprint, request, abort, current_app, jsonify, send_file, redirect, url_for
from flask_security import login_required

# Database
from ..extensions import db, marshmallow as ma
from ..models import (AppApi,
                      AppApiAccess,
                      Events,
                      User,
                      Controller,
                      Reader,
                      Door,
                      Relay,
                      Settings,
                      ControllerSchema)
from marshmallow import fields
from sqlalchemy.exc import IntegrityError, InternalError, DataError, InterfaceError

# Caching
from ..extensions import cache

# Networking
from ..utils.network import NetworkSettings
from ..utils.security import SecuritySettings
from ..utils.mail_utils import EmailSettings
from ..utils.rules import RulesSettings
from ..utils.timezone import TimeZoneSettings
from ..utils.ldap import LDAPSettings, ldap_test
from ..utils.system_info import SystemInfo

# Nginx
import nginx

# Forms
from ..forms import (SettingsNetworkForm,
                     SecuritySettingsForm,
                     SettingsEmailForm,
                     SettingsGlobalTimeForm,
                     SettingsTimeZoneFrom,
                     SettingsLDAPForm)

# Email
from ..extensions import mail
from ..utils.mail_utils import send_email

# LDAP
from ldap3 import Server, Connection, ALL, NTLM

# TimeZone
from ..utils.sys_rtc import ntp_clock_sync, time_zone

# Generators
from ..utils.key_generators import gen_pass_token

# File handing
import gzip
import shutil

# Upgrade
from celery.result import AsyncResult

# Async
from ..tasks import send_async_command, upgrade_modislock, database_restore, database_backup
from celery.exceptions import OperationalError


bp = Blueprint('settings', __name__)

pattern = re.compile(r'^(\D+)_(\D+)_(\d)$')
ALLOWED_EXTENSIONS = {'mod', 'zip'}


def allowed_file(filename):
    """Allowed file extension types that will be accepted on restore

    :param str filename:
    :return str filename:
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _get_request_data(form):
    """Returns a dictionary from multidictionary objects

    return dict list with data from request.form
    request.form comes in multidict [('data[id][field]',value), ...]
    :param form: MultiDict from `request.form`
    :rtype: {id1: {field1:val1, ...}, ...} [fieldn and valn are strings]
    """
    # fill in id field automatically
    data = defaultdict(lambda: {})

    # fill in data[id][field] = value
    for form_key in form.keys():
        if form_key == 'action':
            continue
        data_part, id_part, field_part = form_key.split('[')

        if data_part != 'data':
            raise ValueError("invalid input in request: {}".format(form_key))

        id_value = int(id_part[0:-1])
        field_name = field_part[0:-1]
        data[id_value][field_name] = form[form_key]
    return data  # return decoded result


# def _save_hostname(old_name, new_name):
#     """Saves hostname, reconfigures nginx server, and re-initializes the app APP_ID
#
#     :param str old_name:
#     :param str new_name:
#     :return:
#     """
#     with open('/etc/hostname', 'r') as f:
#         s = f.read()
#
#     if old_name in s:
#         key_args = ['openssl', 'genrsa', '-out', '/var/www/modislock.key', '2048']
#         cert_args = ['openssl', 'req', '-new', '-x509', '-key', '/var/www/modislock.key', '-out',
#                      '/var/www/modislock.cert', '-days', '3650', '-subj']
#
#         # Safely write the changed content, if found in the file
#         with open('/etc/hostname', 'w') as f:
#             s = s.replace(old_name, new_name)
#             f.write(s)
#         new_server_name = new_name + '.local'
#         current_app.config['SITE_DOMAIN'] = 'https://' + new_server_name
#         modis = nginx.loadf('/etc/nginx/sites-available/admin_site')
#         modis.filter('Server')[0].filter('Key', 'server_name')[0].value = new_server_name
#         modis.filter('Server')[1].filter('Key', 'server_name')[0].value = new_server_name
#         nginx.dumpf(modis, '/etc/nginx/sites-available/admin_site')
#         # Generate the key
#         send_async_command.apply_async(args=[key_args])
#
#         # Generate certificate
#         cert_args.append('/CN=' + new_server_name)
#         send_async_command.apply_async(args=[cert_args])


def _save_reader_settings(form):
    """Save reader door and relay settings

    :param form:
    :return:
    """
    new_form = form.to_dict()
    table = next(iter(new_form))
    m = pattern.search(table)
    table = m.group(1)
    id = m.group(3)
    result = False

    if table == 'reader':
        reader = Reader.query.filter(Reader.idreader == id).first()

        if reader is not None:
            try:
                reader.alt_name = form.get(table + '_name_' + id, '')
                reader.location = form.get(table + '_location_' + id, '')
                reader.door_iddoor = int(form.get(table + '_door_' + id, '1'))
                reader.location_direction = 'ENTRY' if form.get(table + '_direction_' + id, False) else 'EXIT'
                reader.enabled = True if form.get(table + '_enabled_' + id, False) else False
            except KeyError as e:
                current_app.logger.debug(e)
                return result
    elif table == 'door':
        door = Door.query.filter(Door.iddoor == int(id)).first()
        relays = Relay.query.filter(Relay.door_iddoor == int(id)).all()

        if len(relays) > 0 and door is not None:
            for relay in relays:
                relay.door_iddoor = None

            try:
                db.session.commit()
            except (InternalError, IntegrityError, InterfaceError) as e:
                db.session.rollback()
                current_app.logger.debug('Error committing to database: {}'.format(e.args[0]))
                return result

        if door is not None:
            try:
                door.alt_name = form.get(table + '_name_' + id, '')
                relays = form.getlist(table + '_assoc_relays_' + id)
            except KeyError as e:
                current_app.logger.debug(e)
                return result
            else:
                for relay in relays:
                    try:
                        assoc = Relay.query.filter(Relay.idrelay == int(relay)).first()
                    except (InternalError, IntegrityError, InterfaceError) as e:
                        current_app.logger.debug('Error in reading database: {}'.format(e.args[0]))
                    else:
                        if assoc is not None:
                            assoc.door_iddoor = int(id)
                            try:
                                db.session.commit()
                            except (InternalError, IntegrityError, InterfaceError) as e:
                                db.session.rollback()
                                current_app.logger.debug('Error in writing database: {}'.format(e.args[0]))
                                return result
                            else:
                                result = True
                result = True
                return result
    elif table == 'relay':
        relay = Relay.query.filter(Relay.idrelay == id).first()

        if relay is not None:
            try:
                relay.enabled = True if form.get(table + '_enable_' + id, False) else False
                relay.delay = int(float(form.get(table + '_delay_' + id, '1.5')) * 1000)
            except KeyError as e:
                current_app.logger.debug(e)
                return result

    try:
        db.session.commit()
    except (InternalError, IntegrityError) as e:
        db.session.rollback()
        current_app.logger.debug('Error committing to database: {}'.format(e.args[0]))
    else:
        result = True

    return result


def _get_reader_settings():
    """Retrieve reader settings
    """
    _devices = Controller.query.filter(Controller.idcontroller == 1).first()
    devices = dict()

    if _devices is not None:
        scheme = ControllerSchema()
        devices = scheme.dump(_devices).data

    return devices


def _backup_age():
    """Backup age since last backup

    :return int:
    """
    last_bu = Settings.query.filter(Settings.settings_name == 'LAST_BACKUP').first()

    if last_bu is not None:
        back_age = (datetime.now() - datetime.strptime(last_bu.settings_value, '%Y-%m-%d')).days
    else:
        back_age = 0

    return back_age


@bp.route('/settings/upgrade/<string:target>')
def system_upgrade(target):
    """Upgrades selected system

    :param str target:

    :return html system_upgrading.html:

    """
    task_id = 0

    if target == 'modislock':
        try:
            task_id = upgrade_modislock.s('modislock').apply_async(countdown=3)
        except OperationalError:
            current_app.logger.debug('Could not upgrade modislock')
    elif target == 'modislock-monitor':
        try:
            task_id = upgrade_modislock.s('modislock-monitor').apply_async(countdown=3)
        except OperationalError:
            current_app.logger.debug('Could not upgrade monitor')
    else:
        task_id = 0

    if task_id == 0:
        return redirect(url_for('settings.settings')), 302
    else:
        return render_template('settings/system_upgrading.html',
                               target=target,
                               task_id=task_id.id,
                               domain=current_app.config.get('SITE_DOMAIN'))


@bp.route('/settings/upgrade_status/<string:task_id>')
def task_status(task_id):
    """Gets the requested task update status

    :param task_id:
    :return:
    """
    task = AsyncResult(task_id)

    response = {'state': 'PENDING', 'message': 'Pending Execution', 'count': 0}

    if task.state == 'FAILURE':
        response['state'] = task.state
        response['message'] = task.info.get('message', '')
        response['count'] = 0
    elif task.state == 'COMPLETE':
        response['state'] = task.state
        response['message'] = task.info.get('message', '')
        response['count'] = task.info.get('count', '')
    elif task.state == 'PROGRESS':
        response['state'] = task.state
        response['message'] = task.info.get('message', '')
        response['count'] = task.info.get('count', '')

    return jsonify(response)


@bp.route('/settings/restart', methods=['POST'])
def task_complete():
    """When a task is complete, restart the required systems

    :return:
    """
    target = request.form.get('target')
    args = ['supervisorctl', 'restart']

    if target == 'modislock':
        args.append('admin:*')
    elif target == 'modislock-monitor':
        args.append('monitor:*')
    elif target == 'modislock-system':
        args = ['systemctl', 'reboot']
        try:
            send_async_command.apply_async(args=[args], countdown=3)
        except OperationalError:
            current_app.logger.debug('Error submitting restart')
    if len(args) > 2:
        try:
            send_async_command.apply_async(args=[args])
        except OperationalError:
            current_app.logger.debug('Error submitting restart')

    return jsonify({'success': 0}), 200


@bp.route('/settings/api_tokens', methods=['GET', 'PUT', 'POST', 'DELETE'])
@login_required
def get_api_tokens():
    """API Token management

    :return:
    """
    re_field = re.compile(r'^data\[\w+\]\[(\w+)\]$')

    if request.method == 'GET':
        api_keys = AppApi.query.join(AppApiAccess, AppApi.app_api_id == AppApiAccess.app_api_app_api_id) \
            .with_entities(AppApi.app_api_id.label('app_id'),
                           AppApiAccess.token,
                           AppApiAccess.expires) \
            .all()

        if api_keys is None:
            return jsonify({'data': []}), 200
        else:
            class ApiKey(ma.Schema):
                app_id = fields.String()
                token = fields.String()
                expires = fields.DateTime(format='%Y-%m-%d %H:%M:%S')

            ret = ApiKey(many=True).dump(api_keys).data

            return jsonify({'data': ret}), 200
    elif request.method == 'POST':
        action = request.form.get('action')

        if action != 'create' or action is None:
            abort(400)

        try:
            action = _get_request_data(request.form.to_dict())
        except ValueError:
            return jsonify({'error': 'ERROR_IN_REQUEST'})

        app_id = action[0].get('app_id')
        app_secret = action[0].get('app_secret')

        existing_app = AppApi.query.filter_by(app_api_id=app_id).first()

        if existing_app:
            error = {
                'code': 'APP_ID_ALREADY_EXISTS'
            }
            return jsonify({'error': error}), 400
        else:
            pwd, exp, tok = gen_pass_token(app_secret)

            app = AppApi(app_api_id=app_id,
                         app_secret=pwd)
            access = AppApiAccess(token=tok,
                                  expires=exp,
                                  app_api_app_api_id=app.app_api_id)
            db.session.add(app)
            db.session.add(access)

            try:
                db.session.commit()
            except (IntegrityError, InternalError, DataError) as e:
                db.session.rollback()
                current_app.logger.debug('Error in database operation {}'.format(e.args[0]))
                return jsonify({'error': 'ERROR_ADDING_TO_DATABASE'})
            else:
                return jsonify({'data': [
                    {'app_id': app_id,
                     'token': tok,
                     'expires': exp
                     }
                ]}), 201
    elif request.method == 'PUT':
        action = request.form.get('action')

        if action != 'edit' or action is None:
            abort(400)

        action = request.form.to_dict()
        form_request = dict()

        for key in action.keys():
            if key == 'action':
                continue
            result = re_field.match(key)
            form_request[result.group(1)] = action[key]

        edit_app = AppApi.query.join(AppApiAccess, AppApi.app_api_id == AppApiAccess.app_api_app_api_id)\
            .filter(AppApi.app_api_id == form_request.get('app_id')).one_or_none()

        if edit_app is not None:
            pwd, exp, tok = gen_pass_token(form_request.get('app_secret'))
            edit_app.app_secret = pwd
            edit_app.token = tok
            edit_app.expires = exp
            try:
                db.session.commit()
            except (IntegrityError, InternalError, DataError) as e:
                db.session.rollback()
                current_app.logger.debug('Error in database operation {}'.format(e.args[0]))
                return jsonify({'error': 'COULD_NOT_COMMIT_CHANGES'})

            return jsonify({'data': [{
                'app_id': edit_app.app_api_id,
                'token': edit_app.token,
                'expires': edit_app.expires
            }]}), 200
    elif request.method == 'DELETE':
        action = request.args.get('action')

        if action != 'remove' or action is None:
            abort(400)

        action = request.args.to_dict()
        arg_request = dict()

        for key in action.keys():
            if key == 'action':
                continue
            result = re_field.match(key)
            arg_request[result.group(1)] = action[key]

        del_app = AppApi.query.filter_by(app_api_id=arg_request.get('app_id')).one_or_none()

        if del_app is not None:
            db.session.delete(del_app)

            try:
                db.session.commit()
            except (InternalError, IntegrityError) as e:
                current_app.logger.error('Count not delete record from database: {}'.format(e.args[0]))
                return jsonify({'error': 'COULD_NOT_DELETE_RECORD'})
            else:
                return jsonify({}), 204
        else:
            abort(400)


@bp.route('/settings/reboot')
@login_required
def reboot():
    return render_template('settings/system_rebooting.html',
                           domain=current_app.config.get('SITE_DOMAIN'))


@bp.route('/settings/restore', methods=['POST'])
@login_required
def restore_db():
    global task_restore

    assert 'file' in request.files
    upload_file = request.files['file']

    if allowed_file(upload_file.filename):
        upload_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], upload_file.filename))
        upload_file = os.path.join(current_app.config['UPLOAD_FOLDER'], upload_file.filename)
        task_restore = database_restore.apply_async(args=[upload_file])

        return jsonify({'success': 'restore started'}), 200

    else:
        return jsonify({'error': 'Not a valid file'}), 400


@bp.route('/settings/status/<string:task_id>')
@login_required
def get_task_status(task_id):

    task = AsyncResult(task_id)

    if task.ready():
        response = {'state': task.state, 'message': task.result}
        return jsonify(response)
    else:
        return jsonify({'FAILURE': 'Empty task'}), 400


@bp.route('/settings/get_backup/<string:filename>')
@login_required
def get_backup(filename):
    """Get the lastest backup

    :param str filename:
    :return:
    """
    if os.path.exists('/tmp/' + filename):
        return send_file('/tmp/' + filename,
                         as_attachment=True,
                         attachment_filename='lock' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '.mod')
    else:
        return jsonify({'error': 'Error no file'})


@bp.route('/settings', methods=['GET', 'POST'])
def settings():
    """Settings page

    :return:
    """
    network_form = SettingsNetworkForm()
    security_form = SecuritySettingsForm()
    email_form = SettingsEmailForm()
    rules_form = SettingsGlobalTimeForm()
    timezone_form = SettingsTimeZoneFrom()
    ldap_form = SettingsLDAPForm()

    if request.method == 'POST':
        form_type = ''

        for thing in request.form:
            if 'submit' in thing:
                form_type = thing.split('_')[1]
                break
            if 'action' in thing:
                form_type = 'action'
                break

        if form_type == 'reader' or form_type == 'door' or form_type == 'relay':
            result = _save_reader_settings(request.form)
            return jsonify({'success' if result else 'error': 'updated reader' if result else 'could not update'}), 200 if result else 400
        elif form_type == 'network':
            if network_form.validate():
                NetworkSettings(network_form)
                return jsonify({'success': 'saved network settings'}), 200
            return jsonify({'error': network_form.errors}), 400
        elif form_type == 'email':
            if email_form.validate():
                EmailSettings(email_form)
                return jsonify({'success': 'saved email settings'}), 200
            return jsonify({'error': email_form.errors}), 400
        elif form_type == 'security':
            if security_form.validate():
                SecuritySettings(security_form)
                return jsonify({'success': 'saved security settings'}), 200
            return jsonify({'error': security_form.errors}), 400
        elif form_type == 'ldap':
            if ldap_form.validate():
                if ldap_test(request.form):
                    LDAPSettings(ldap_form)
                    return jsonify({'success': 'saved ldap settings'}), 200
            return jsonify({'error': ldap_form.errors}), 400
        elif form_type == 'rules':
            if rules_form.validate():
                RulesSettings(rules_form)
                return jsonify({'success': 'saved rules settings'}), 200
            return jsonify({'error': rules_form.errors}), 400
        elif form_type == 'action':
            action = request.form.get('action')

            if action == 'backup':
                try:
                    t_backup = database_backup.apply_async()
                except OperationalError:
                    return jsonify({'error': 'Unable to start backup'}), 400
                else:
                    return jsonify({'success': 'starting backup', 'task_id': t_backup.id}), 200
            elif action == 'restore':
                try:
                    t_restore = database_restore.apply_async(args=[])
                except OperationalError:
                    return jsonify({'error': 'Unable to start restore'}), 400
                else:
                    return jsonify({'success': 'starting restore', 'task_id': t_restore.id})
            elif action == 'reboot':
                send_async_command.apply_async(args=['systemctl', 'reboot'], countdown=3)
                return jsonify({'success': 'system rebooting'}), 200
            elif action == 'purge':
                Events.query.delete()

                try:
                    db.session.commit()
                except (InternalError, IntegrityError):
                    db.session.rollback()
                    current_app.logger.error('ERROR: Purging events from database failed')
                    return jsonify({'error': 'unable to purge'}), 400
                else:
                    current_app.logger.info('Purged all events from database')
                    return jsonify({'success': 'purged history'}), 200

    network_form.process(obj=NetworkSettings())
    security_form.process(obj=SecuritySettings())
    email_form.process(obj=EmailSettings())
    rules_form.process(obj=RulesSettings())
    timezone_form.process(obj=TimeZoneSettings())
    ldap_form.process(obj=LDAPSettings())

    forms = {'network': network_form,
             'security': security_form,
             'email': email_form,
             'rules': rules_form,
             'timezone': timezone_form,
             'ldap': ldap_form}

    data = {'bu_age': _backup_age(),
            'devices': _get_reader_settings(),
            'software': SystemInfo.get_software_versions()}

    return render_template('settings/settings.html', forms=forms, data=data)

