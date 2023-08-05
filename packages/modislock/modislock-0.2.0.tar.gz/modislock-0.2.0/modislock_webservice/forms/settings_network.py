# coding: utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, IPAddress, Optional


class SettingsNetworkForm(FlaskForm):
    """Network settings

    """
    host_name = StringField(description='Host Name',
                            validators=[DataRequired(message='Host name required')])
    mac_address = StringField(description='Mac Address', validators=[Optional()])
    dhcp_mode = BooleanField(description='IP Mode')
    ip_address = StringField(description='Lock IP',
                             validators=[DataRequired(message='IP Address required'),
                                         IPAddress(message='Must match IPV4 format')])
    sub_address = StringField(description='Subnet',
                              validators=[DataRequired(message='Subnet Address required'),
                                          IPAddress(message='Must match IPV4 format')])
    gw_address = StringField(description='Gateway',
                             validators=[DataRequired(message='Gateway Address required'),
                                         IPAddress(message='Must match IPV4 format')])
    dns_address = StringField(description='DNS',
                              validators=[DataRequired(message='DNS Address required'),
                                          IPAddress(message='Must match IPV4 format')])
    submit_network_btn = SubmitField(label='Save Network Settings')

    def validate(self):
        if self.dhcp_mode.data:
            return True
        else:
            return super(SettingsNetworkForm, self).validate()
            # return self.FlaskForm.validate(self)
