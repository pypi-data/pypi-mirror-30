# coding: utf-8
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, BooleanField


class SecuritySettingsForm(FlaskForm):
    """Security settings are things that define how long data will be preserved, how many digits the PIN codes
    will have and what events does the administrator need to be notified.
    """
    months_preserved = SelectField(description='Data Preserve',
                                   choices=[('1', '1 Month'), ('2',  '2 Months'), ('3', '3 Months'), ('4', '4 Months')])
    pin_places = SelectField(description='Pin Length',
                             choices=[('4', '4 Places'), ('5', '5 Places'), ('6', '6 Places'), ('7', '7 Places')])

    ssh_access = BooleanField(description='SSH Access')

    submit_security_btn = SubmitField('Save Security')
