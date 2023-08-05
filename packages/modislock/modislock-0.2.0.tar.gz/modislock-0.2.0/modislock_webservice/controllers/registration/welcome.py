# coding: utf-8
from flask import render_template, Blueprint, request, current_app

# Subprocessing for restarting supervisor
from ...tasks import send_async_command
from celery.exceptions import OperationalError

# Form
from forms.welcome import WelcomeForm

# Security
from flask_security.utils import hash_password

# Database
from ...models import User, Host
from sqlalchemy.exc import IntegrityError, InternalError

# Date time
from datetime import datetime
from ...utils.sys_rtc import ntp_clock_sync, time_zone, system_time
from ...utils.sys_ssh import system_ssh
from ...extensions import db

bp = Blueprint('welcome', __name__)


def save_reg_data(form):
    """Save registration data to database

    :param form:
    :return:
    """
    # Serial Number
    user = User.query.filter(User.id == 1).first()
    host = Host.query.filter(Host.idhost == 1).first()

    if (host is not None) and (user is not None):
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.password = hash_password(form.password.data)

        host.serial_number = form.serial_number.data
        host.registered = True
        host.installation_date = datetime.now()
        host.host_name = 'modislock'

    else:
        user = User(id=1,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    password=hash_password(form.password.data))
        host = Host(idhost=1,
                    serial_number=form.serial_number.data,
                    registered=True,
                    installation_date=datetime.now(),
                    host_name='modislock')
        db.session.add(user)
        db.session.add(host)

    try:
        db.session.commit()
    except (IntegrityError, InternalError):
        current_app.logger.debug('Error writing to database')
        db.session.rollback()
        return False

    # Timezone and Time
    if time_zone() != form.tz_zone.data:
        time_zone(tzone=form.tz_zone.data)

    if ntp_clock_sync() != form.auto_time.data:
        ntp_clock_sync(enabled=form.auto_time.data)

    if not form.auto_time.data:
        try:
            system_time(time_date=form.sys_time.data)
        except TypeError:
            current_app.logger.debug('Wrong format for system setting')

    # if system_ssh() != form.ssh_enable.data:
    #     system_ssh(enabled=form.ssh_enable.data)

    if form.ldap_enable.data:
        # TODO Enabled LDAP
        pass

    if form.battery_enable.data:
        # TODO Enable Battery
        pass

    if form.database_bu_enable.data:
        # TODO Enable Database Backup
        pass

    return True


@bp.route('/', methods=['GET', 'POST'])
def welcome():
    """Registration Page

    Controls the initial registration window(s).
    1. Serial Number
    2. Admin email address
    3. Admin password
    4. System Time Date Timezone
    5. Timezone

    :returns html_template welcome.html:
    """
    form = WelcomeForm()

    if request.method == 'POST':
        if form.validate():
            # noinspection PyTypeChecker
            if save_reg_data(form):
                args = ['supervisorctl', 'restart', 'admin:modis_admin']
                try:
                    send_async_command.apply_async(args, countdown=3)
                except OperationalError:
                    pass
                return render_template('welcome/birthing_new_lock.html', domain=current_app.config.get('SITE_DOMAIN'))
        else:
            current_app.logger.error('Could not validate registration form')

    form.tz_zone.data = time_zone()
    form.sys_time.data = datetime.now().strftime('%H:%M:%S %Y-%m-%d')
    form.auto_time.data = ntp_clock_sync()
    form.ssh_enable.data = system_ssh()
    form.ldap_enable.data = False
    form.battery_enable.data = False
    form.database_bu_enable.data = False

    return render_template('welcome/welcome.html', form=form)
