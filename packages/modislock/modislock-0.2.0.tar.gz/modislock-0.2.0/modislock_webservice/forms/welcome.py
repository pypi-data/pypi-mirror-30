# coding: utf-8

from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import Email, InputRequired, Length, ValidationError
import re

# Existing form
from .settings_timezone import SettingsTimeZoneFrom


def email_validate(form, field):
    email_test = re.match("^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$", form.email.data)
    if email_test is None:
        raise ValidationError(message='Enter a valid email address')

str_terms = 'End-User License Agreement ("Agreement")\n' \
            'Last updated: Jan 12, 2018\n' \
            'Please read this End-User License Agreement ("Agreement") carefully before clicking the "I Agree" button or using the Modis Lock ' \
            'By clicking the "I Agree" button, by using the Modis Lock, you are agreeing to be bound by the terms and conditions of this Agreement.' \
            'If you do not agree to the terms of this Agreement, do not click on the "I Agree" button and do not use the Modis Lock.'


class WelcomeForm(SettingsTimeZoneFrom):
    """WelcomeForm Registration Data

    """

    serial_number = StringField(label='Serial Number', description='Serial Number', 
                                validators=[InputRequired(message='Enter a valid serial number')],
                                render_kw={"placeholder": "00000000"})

    auto_time = BooleanField(label='Automatic Time Synchronization')
    ssh_enable = BooleanField(label='SSH Access')
    ldap_enable = BooleanField(label='LDAP Integration')
    battery_enable = BooleanField(label='Battery Backup Monitor')
    database_bu_enable = BooleanField(label='Automatic Database Backup')

    first_name = StringField(label='First Name', description='First Name',
                             validators=[InputRequired(message='First Name Required'),
                                         Length(max=40)])

    last_name = StringField(label='Last Name', description='Last Name',
                            validators=[InputRequired(message='Last Name Required'),
                                        Length(max=40)])

    email = StringField(label='Email Address',
                        description='Administrator Email Address',
                        validators=[InputRequired(message='Email Required'),
                                    Length(max=60), email_validate])

    password = PasswordField(label='Admin Password', description='Administrator Password',
                             validators=[InputRequired(message='Password Required'),
                                         Length(max=20)])

    pwd_confirm = PasswordField(label='Password Confirm', description='Administrator Password Confirmation',
                                validators=[InputRequired(message='Password Required'),
                                            Length(max=20)])

    terms_agree = BooleanField(label='Agree with Terms')

    terms = TextAreaField(label='Terms and Conditions', default=str_terms)

    submit_btn = SubmitField(label='Submit Data', description='Submit Data')
