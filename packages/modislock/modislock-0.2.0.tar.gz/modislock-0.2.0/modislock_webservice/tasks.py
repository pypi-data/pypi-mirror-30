# coding: utf-8

from flask import current_app
from .extensions import celery, mail, db
from flask_mail import Message, BadHeaderError
from subprocess import Popen, PIPE, CalledProcessError, TimeoutExpired, run
from celery.utils.log import get_task_logger
from celery.states import FAILURE, SUCCESS, PENDING, STARTED, REJECTED

# LDAP
from ldap3 import Server, Connection, ALL, NTLM

from .models import Settings, User
from sqlalchemy.exc import InternalError, InterfaceError, OperationalError

import re
import os
from simplecrypt import encrypt, decrypt
from .utils.system_info import SystemInfo
from datetime import datetime
import random
import string
import binascii

from threading import Timer


logger = get_task_logger(__name__)

database_pattern = re.compile(r'[/]{2}([\w]+):([\w]+)@([a-zA-Z0-9._\-]+)/([\w]+)')
dump_pattern = re.compile(r'^-- Dump completed on (\d{4}-\d{2}-\d{2} {1,2}\d{1,2}:\d{2}:\d{2})$')


def crc32_from_file(filename):
    with open(filename, 'rb') as f_in:
        buf = f_in.read()
        buf = (binascii.crc32(buf) & 0xFFFFFFFF)
    return "%08X" % buf


def backup_cleanup(filename):
    if os.path.exists(filename):
        os.remove(filename)


class BaseTask(celery.Task):
    """Abstract base class for all tasks in my app."""

    abstract = True

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Log the exceptions to sentry at retry."""
        # sentrycli.captureException(exc)
        super(BaseTask, self).on_retry(exc, task_id, args, kwargs, einfo)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Log the exceptions to sentry."""
        # sentrycli.captureException(exc)
        super(BaseTask, self).on_failure(exc, task_id, args, kwargs, einfo)


@celery.task(bind=True)
def upgrade_modislock(self, package, version=None):
    """Upgrades specified modules in a background task.

    :param self:
    :param str package:
    :param str version:
    :return:
    """
    logger.info('Package: {} Version: {}'.format(package, version))

    if not isinstance(package, (str, bytearray)):
        return {'state': 'FAILURE', 'message': 'Bad package type:'.format(type(package))}
    if version:
        if not isinstance(version, (str, bytearray)):
            return {'state': 'FAILURE', 'message': 'Bad version'}

    args = ['pip3', 'install', '--upgrade', package]
    process = Popen(args, stdout=PIPE, stderr=PIPE)
    message_cnt = 0
    error_cnt = 0

    while True:
        output = process.stdout.readline()

        if output and output != '':
            if re.search('error', output, re.IGNORECASE):
                error_cnt += 1

            self.update_state(state=PENDING,
                              meta={'count': message_cnt, 'errors': error_cnt,
                                    'message': output.decode('utf-8').strip()})
            message_cnt += 1
        if process.poll() is not None:
            break

    return {'count': message_cnt, 'errors': error_cnt, 'message': 'update finished', 'state': 'COMPLETE'}


@celery.task()
def send_async_command(cmd):
    logger.info('Commands: {}'.format(cmd))
    error = b''

    try:
        cmd = Popen(cmd, stdout=PIPE, stderr=PIPE, timeout=60)
        stdout, error = cmd.communicate()
    except (CalledProcessError, TimeoutExpired):
        return {'error': error.decode('utf-8')}
    else:
        return {"result": stdout.decode('utf-8')}


@celery.task()
def send_async_email(msg_dict):
    msg = Message()
    msg.__dict__.update(msg_dict)
    mail.send(msg)


@celery.task(bind=True, max_retries=3, soft_time_limit=5)
def send_security_email(self, **kwargs):
    try:
        mail.send(Message(**kwargs))
    except Exception as e:
        self.retry(countdown=10, exc=e)


@celery.task(bind=True)
def database_backup(self):
    """Database backup task.

    :param self:
    :return:
    """
    filename = ''.join(random.choice(string.ascii_letters) for m in range(16))
    tmp_db = '/tmp/db_backup.sql'
    tmp_db2 = '/tmp/' + filename

    if os.path.exists(tmp_db):
        os.remove(tmp_db)
    self.update_state(state=STARTED, meta={'message': 'database backup started'})

    db_config = current_app.config.get('SQLALCHEMY_DATABASE_URI')
    m = database_pattern.search(db_config)
    # args = ['mysqldump', '-u', m.group(1), '-p' + m.group(2), '-h', m.group(3), '--databases', m.group(4)]
    cmd = 'mysqldump -u root -h {} {} --routines --events --triggers > {}'.format(m.group(3), m.group(4), tmp_db)

    try:
        p = Popen(cmd, shell=True)
        p.communicate()
    except OSError:
        self.update_state(state=FAILURE, meta={'message': 'file does not exist'})
        return
    # Update status, stage 1
    self.update_state(state=PENDING, meta={'stage': 1, 'message': 'finished database dump'})
    current_app.logger.debug('Database Dumped')

    with open(tmp_db, 'r') as f_in:
        buf = f_in.read().splitlines()
        # TODO Fails on empty file -> IndexError
        last_line = buf[-1]

        if dump_pattern.match(last_line):
            m = dump_pattern.search(last_line)
            if datetime.strptime(m.group(1), '%Y-%m-%d %H:%M:%S') > datetime.now():
                self.update_state(state=FAILURE, meta={'message': 'incorrect timestamp on dump'})
                current_app.logger.debug('Invalid timestamp on dump file')
                return
        else:
            self.update_state(state=FAILURE, meta={'message': 'incorrect timestamp on dump'})
            current_app.logger.debug('Not complete dump, no timestamp:\r\nFound: {}'.format(last_line))
            return
        # Save some memory
        del buf

    current_app.logger.debug('Backup was complete and valid')
    crc = crc32_from_file(tmp_db)

    with open(tmp_db, 'a') as f_in:
        f_in.write('-- ' + crc)

    current_app.logger.debug('CRC: 0x{}'.format(crc))
    self.update_state(state=PENDING, meta={'stage': 2, 'message': 'database crc complete'})

    with open(tmp_db, 'r') as f_in:
        content = f_in.read()
    with open(tmp_db2, 'wb') as f_out:
        f_out.write(encrypt(SystemInfo.get_cpu_serial(), content))
    # Save some memory
    del content
    current_app.logger.debug('Database file encrypted')
    # Update Status
    self.update_state(state=PENDING, meta={'stage': 3, 'message': 'database encrypted'})
    # Compress newly encrypted file
    current_app.logger.debug('Database Compressed')

    if os.path.exists(tmp_db):
        os.remove(tmp_db)

    current_app.logger.debug('Database is backup complete')
    last_bu = Settings.query.filter(Settings.settings_name == 'LAST_BACKUP').first()

    if last_bu is not None:
        last_bu.settings_value = datetime.now().strftime('%Y-%m-%d')

        try:
            db.session.commit()
        except (InternalError, InterfaceError, OperationalError):
            db.session.rollback()

    Timer(60, backup_cleanup, args=[tmp_db2]).start()
    self.update_state(state=PENDING, meta={'stage': 4, 'message': 'database backup complete'})

    return {'message': 'database backup complete', 'file': filename}


@celery.task(bind=True)
def database_restore(self, file_name):
    """Restore database from previous backup

    :param self:
    :param str file_name:
    :return:
    """
    tmp_db = '/tmp/db_backup.sql'
    file = os.path.join(current_app.config['UPLOAD_FOLDER'], file_name)

    self.update_state(state=STARTED, meta={'message': 'database restore started'})

    if not os.path.exists(file):
        current_app.logger.debug('File provided for restore does not exist')
        self.update_state(state=FAILURE, meta={'message': 'file does not exist'})
        return

    self.update_state(state=PENDING, meta={'stage': 1, 'message': 'restore file found'})
    try:
        with open(file, 'rb') as f_in:
            content = f_in.read()
            with open(tmp_db, 'wb') as f_out:
                f_out.write(decrypt(SystemInfo.get_cpu_serial(), content))
    except (IOError, FileNotFoundError):
        current_app.logger.debug('Invalid file')
        self.update_state(state=FAILURE, meta={'message': 'file could not be decrypted'})
        return
    else:
        self.update_state(state=PENDING, meta={'stage': 2, 'message': 'database decrypted'})

    if os.path.exists(file):
        os.remove(file)

    with open(tmp_db, 'r') as f_in:
        content = f_in.readlines()

    lastline = content[-1]

    with open(tmp_db, 'w') as f_out:
        f_out.writelines([line for line in content[:-1]])

    crc = crc32_from_file(tmp_db)
    oldcrc = lastline.split(' ')

    if crc != oldcrc[1]:
        current_app.logger.debug('Bad CRC')
        self.update_state(state=FAILURE, meta={'message': 'failed crc check'})
        return

    db_config = current_app.config.get('SQLALCHEMY_DATABASE_URI')
    m = database_pattern.search(db_config)
    cmd = 'mysql -u root -h {} {} < {}'.format(m.group(3), m.group(4), tmp_db)
    # TODO Stop monitor and any connections to the database from web interface, otherwise will timeout
    try:
        p = run(cmd, shell=True, timeout=60)
    except (OSError, TimeoutExpired):
        self.update_state(state=FAILURE, meta={'message': 'restore process error'})
    else:
        if os.path.exists(tmp_db):
            os.remove(tmp_db)
        self.update_state(state=PENDING, meta={'state_count': 3, 'message': 'database restored'})


@celery.task(bind=True)
def import_ldap_users(self):
    """Import users from LDAP connection

    :param self:
    :return:
    """
    ldap_enabled = Settings.query.filter(Settings.settings_name == 'LDAP_ENABLED').first()

    if ldap_enabled is not None:
        ldap_enabled = True if ldap_enabled.settings_value == 'True' else False

        if ldap_enabled:
            ldap_params = Settings.query.filter(Settings.settings_name.like('LDAP%')).all()
            settings = dict()

            for params in ldap_params:
                if params.units == 'INT':
                    value = int(params.settings_value)
                elif params.units == 'BOOL':
                    value = True if params.settings_value == 'True' else False
                else:
                    value = params.settings_value
                settings[params.settings_name] = value

            search_params = {
                'search_base': settings['LDAP_GROUP_DN'] + ',' + settings['LDAP_BASE_DN'],
                'search_filter': settings['LDAP_USER_OBJECT_FILTER'],
                'attributes': [settings['LDAP_MAPPING_USERNAME'],
                               settings['LDAP_MAPPING_F_NAME'],
                               settings['LDAP_MAPPING_L_NAME'],
                               settings['LDAP_MAPPING_EMAIL']]
            }

            server = Server(host=settings['LDAP_HOST'],
                            port=settings['LDAP_PORT'],
                            use_ssl=settings['LDAP_USE_SSL'],
                            get_info=ALL)
            conn = Connection(server=server,
                              user=settings['LDAP_BIND_USER_DN'],
                              password=settings['LDAP_BIND_USER_PASSWORD'],
                              authentication=NTLM if settings['LDAP_USE_MS_AD'] else None)
            self.update_state(state=PENDING, meta={'stage': 1, 'message': 'parameters applied'})

            try:
                conn.bind()
            except:
                pass
            else:
                self.update_state(state=PENDING, meta={'stage': 2, 'message': 'connected to server'})
                conn.search(**search_params)
                entry_count = len(conn.entries)
                self.update_state(state=PENDING, meta={'stage': 3,
                                                       'message': 'search complete',
                                                       'records': entry_count})

                for entry in conn.entries:
                    attrib = entry.entry_attributes_as_dict
                    uid = settings['LDAP_MAPPING_USERNAME']
                    first_name = settings['LDAP_MAPPING_F_NAME']
                    last_name = settings['LDAP_MAPPING_L_NAME']
                    email = settings['LDAP_MAPPING_EMAIL']

                    user = User.query.filter(User.uid == attrib[uid]).first()

                    if user is None:
                        user = User(uid=attrib[uid],
                                    first_name=attrib[first_name],
                                    last_name=attrib[last_name],
                                    email=attrib[email])
                        db.session.add(user)

                        try:
                            db.session.commit()
                        except (InternalError, InterfaceError, OperationalError):
                            db.session.rollback()
                    entry_count -= 1
                    self.update_state(state=PENDING, meta={'stage': 4,
                                                           'message': 'entry added',
                                                           'records': entry_count})
                conn.unbind()
                self.update_state(state=SUCCESS, meta={'stage': 5, 'message': 'records imported'})
        else:
            # Ldap not enabled
            self.update_state(state=FAILURE, meta={'message': 'LDAP not enabled'})
    else:
        # Database error ldap enable not found
        self.update_state(state=FAILURE, meta={'message': 'database error ldap enable not found'})


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    pass


__all__ = ['send_security_email', 'send_async_command', 'send_async_email', 'upgrade_modislock',
           'database_backup', 'database_restore', 'import_ldap_users']
