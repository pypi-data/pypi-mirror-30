from flask import current_app, render_template
from flask_mail import Message
from ..tasks import send_async_email
from celery.exceptions import OperationalError, TimeoutError
from ..extensions import db
from ..models import Settings
from sqlalchemy.exc import IntegrityError, InternalError, OperationalError


def _msg_to_dict(to, subject, template, **kwargs):
    """Converts a Message object into a dictionary for the purpose of sending the message to an async task.

    :param str to:
    :param str subject:
    :param html template:
    :param kwargs:
    :return dict:
    """
    app = current_app._get_current_object()

    msg = Message(
        subject=app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject,
        sender=app.config['MAIL_DEFAULT_SENDER'],
        recipients=[to]
    )

    msg.body = render_template('email_templates/' + template + '.txt', **kwargs)
    msg.html = render_template('email_templates/' + template + '.html', **kwargs)

    return msg.__dict__


def send_email(to, subject, template, **kwargs):
    """Send email through async task

    :param to:
    :param subject:
    :param template:
    :param kwargs:

    :return:
    """
    try:
        send_async_email.delay(_msg_to_dict(to, subject, template, **kwargs))
    except (OperationalError, TimeoutError):
        raise IOError


class EmailSettings:
    """
    mail_server = StringField(description='Server',
                              validators=[DataRequired(message='Server address cannot be left blank')])
    mail_port = IntegerField(description='Port',
                             validators=[DataRequired(message='Server port cannot be left blank'),
                                         NumberRange(min=25, max=3535, message='Valid port numbers are from 25 to 3535')])
    mail_use_tls = BooleanField(description='Use TLS')
    mail_use_ssl = BooleanField(description='Use SSL')
    mail_username = StringField(description='User Name',
                                validators=[DataRequired('Username required for server authentication')])
    # PasswordField changed to string field so we could populate the password input
    mail_password = StringField(description='Password',
                                widget=PasswordInput(hide_value=False),
                                validators=[DataRequired(message='Password required')])
    mail_sender = StringField(description='Sender',
                              validators=[DataRequired(message='Sender email address cannot be left blank'),
                                          Email(message='Needs to be a valid email address')])
    notify_on_denied = BooleanField(description='Notify on Denied')
    notify_on_after_hours = BooleanField(description='Notify on After Hours')
    notify_on_system_error = BooleanField(description='Notify on System Error')
    notify_on_power = BooleanField(description='Notify on Power Outage')
    notify_on_door_prop = BooleanField(description='Notify on Door Proped Open')
    """

    def __init__(self, form=None):
        if form is not None:
            for name in dir(form):
                if not name.startswith('_'):
                    unbound_field = getattr(form, name)
                    if hasattr(self, name):
                        setattr(self, name, unbound_field.data)

    @property
    def mail_server(self):
        svr = Settings.query.filter(Settings.settings_name == 'MAIL_SERVER').first()

        if svr is not None:
            return svr.settings_value
        else:
            return 'modis.mail.net'

    @mail_server.setter
    def mail_server(self, address):
        svr = Settings.query.filter(Settings.settings_name == 'MAIL_SERVER').first()

        if svr is not None:
            svr.settings_value = address

            try:
                db.session.commit()
            except (IntegrityError, InternalError, OperationalError):
                db.session.rollback()
            else:
                current_app.config['MAIL_SERVER'] = address
                current_app.logger.debug('Saved mail server')

    @property
    def mail_port(self):
        port = Settings.query.filter(Settings.settings_name == 'MAIL_PORT').first()

        if port is not None:
            try:
                num = int(port.settings_value)
            except ValueError:
                num = 0

            return num
        else:
            return 0

    @mail_port.setter
    def mail_port(self, port_num):
        port = Settings.query.filter(Settings.settings_name == 'MAIL_PORT').first()

        if port is not None:
            port.settings_value = str(port_num)

            try:
                db.session.commit()
            except (IntegrityError, InternalError, OperationalError):
                db.session.rollback()

    @property
    def mail_use_tls(self):
        tls = Settings.query.filter(Settings.settings_name == 'MAIL_USE_TLS').first()

        if tls is not None:
            return True if tls.settings_value == 'True' else False
        else:
            return False

    @mail_use_tls.setter
    def mail_use_tls(self, enable):
        tls = Settings.query.filter(Settings.settings_name == 'MAIL_USE_TLS').first()

        if tls is not None:
            tls.settings_value = 'True' if enable else 'False'

            try:
                db.session.commit()
            except (IntegrityError, InternalError, OperationalError):
                db.session.rollback()

    @property
    def mail_use_ssl(self):
        ssl = Settings.query.filter(Settings.settings_name == 'MAIL_USE_SSL').first()

        if ssl is not None:
            return True if ssl.settings_value == 'True' else False
        else:
            return False

    @mail_use_ssl.setter
    def mail_use_ssl(self, enable):
        ssl = Settings.query.filter(Settings.settings_name == 'MAIL_USE_SSL').first()

        if ssl is not None:
            ssl.settings_value = 'True' if enable else 'False'

            try:
                db.session.commit()
            except (IntegrityError, InternalError, OperationalError):
                db.session.rollback()

    @property
    def mail_username(self):
        username = Settings.query.filter(Settings.settings_name == 'MAIL_USERNAME').first()

        return '' if username is None else username.settings_value

    @mail_username.setter
    def mail_username(self, name):
        username = Settings.query.filter(Settings.settings_name == 'MAIL_USERNAME').first()

        if username is not None:
            username.settings_value = name

            try:
                db.session.commit()
            except (IntegrityError, InternalError, OperationalError):
                db.session.rollback()

    @property
    def mail_password(self):
        password = Settings.query.filter(Settings.settings_name == 'MAIL_PASSWORD').first()

        return '' if password is None else password.settings_value

    @mail_password.setter
    def mail_password(self, pwd):
        password = Settings.query.filter(Settings.settings_name == 'MAIL_PASSWORD').first()

        if password is not None:
            password.settings_value = pwd

        try:
            db.session.commit()
        except (IntegrityError, InternalError, OperationalError):
            db.session.rollback()

    @property
    def mail_sender(self):
        sender = Settings.query.filter(Settings.settings_name == 'MAIL_SENDER').first()

        return '' if sender is None else sender.settings_value

    @mail_sender.setter
    def mail_sender(self, send):
        sender = Settings.query.filter(Settings.settings_name == 'MAIL_SENDER').first()

        if sender is not None:
            sender.settings_value = send

            try:
                db.session.commit()
            except (IntegrityError, InternalError, OperationalError):
                db.session.rollback()

    @property
    def notify_on_denied(self):
        denied = Settings.query.filter(Settings.settings_name == 'NOTIFY_ON_DENIED').first()

        return False if (denied is None or denied.settings_value == 'False') else True

    @notify_on_denied.setter
    def notify_on_denied(self, enable):
        denied = Settings.query.filter(Settings.settings_name == 'NOTIFY_ON_DENIED').first()

        if denied is not None:
            denied.settings_value = 'True' if enable else 'False'

            try:
                db.session.commit()
            except (IntegrityError, InternalError, OperationalError):
                db.session.rollback()

    @property
    def notify_on_after_hours(self):
        after = Settings.query.filter(Settings.settings_name == 'NOTIFY_ON_AFTER_HOURS').first()

        return False if (after is None or after.settings_value == 'False') else True

    @notify_on_after_hours.setter
    def notify_on_after_hours(self, enable):
        after = Settings.query.filter(Settings.settings_name == 'NOTIFY_ON_AFTER_HOURS').first()

        if after is not None:
            after.settings_value = 'True' if enable else 'False'

            try:
                db.session.commit()
            except (IntegrityError, InternalError, OperationalError):
                db.session.rollback()

    @property
    def notify_on_system_error(self):
        sys_error = Settings.query.filter(Settings.settings_name == 'NOTIFY_ON_SYSTEM_ERROR').first()

        return False if (sys_error is None or sys_error.settings_value == 'False') else True

    @notify_on_system_error.setter
    def notify_on_system_error(self, enable):
        sys_error = Settings.query.filter(Settings.settings_name == 'NOTIFY_ON_SYSTEM_ERROR').first()

        if sys_error is not None:
            sys_error.settings_value = 'True' if enable else 'False'

            try:
                db.session.commit()
            except (IntegrityError, InternalError, OperationalError):
                db.session.rollback()

    @property
    def notify_on_power(self):
        power = Settings.query.filter(Settings.settings_name == 'NOTIFY_ON_POWER_FAIL').first()

        return False if (power is None or power.settings_value == 'False') else True

    @notify_on_power.setter
    def notify_on_power(self, enable):
        power = Settings.query.filter(Settings.settings_name == 'NOTIFY_ON_POWER_FAIL').first()

        if power is not None:
            power.settings_value = 'True' if enable else 'False'

            try:
                db.session.commit()
            except (IntegrityError, InternalError, OperationalError):
                db.session.rollback()

    @property
    def notify_on_door_prop(self):
        door = Settings.query.filter(Settings.settings_name == 'NOTIFY_ON_DOOR_PROP').first()

        return False if (door is None or door.settings_value == 'False') else True

    @notify_on_door_prop.setter
    def notify_on_door_prop(self, enable):
        door = Settings.query.filter(Settings.settings_name == 'NOTIFY_ON_DOOR_PROP').first()

        if door is not None:
            door.settings_value = 'True' if enable else 'False'

            try:
                db.session.commit()
            except (IntegrityError, InternalError, OperationalError):
                db.session.rollback()
