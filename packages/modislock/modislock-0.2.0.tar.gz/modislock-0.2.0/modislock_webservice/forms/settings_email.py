# coding: utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField
from wtforms.widgets import PasswordInput
from wtforms.validators import DataRequired, Email, NumberRange


class SettingsEmailForm(FlaskForm):
    """Settings for email notifications

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
    notify_on_denied = BooleanField(description='Notify on Denied Attempt')
    notify_on_after_hours = BooleanField(description='Notify on After Hours Access')
    notify_on_system_error = BooleanField(description='Notify on System Error')
    notify_on_power = BooleanField(description='Notify on Power Outage')
    notify_on_door_prop = BooleanField(description='Notify on Door Propped Open')

    submit_email_btn = SubmitField('Save Email')
