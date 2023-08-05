# coding: utf-8
from flask import Blueprint, render_template, jsonify

# Database
from ..forms import SettingsNetworkForm, SecuritySettingsForm, SettingsEmailForm, SettingsGlobalTimeForm
from sqlalchemy import and_


bp = Blueprint('test', __name__)


@bp.route('/test')
def show_test():

    print('Happy')
    temps = 12

    network_form = SettingsNetworkForm()
    security_form = SecuritySettingsForm()
    email_form = SettingsEmailForm()
    rules_form = SettingsGlobalTimeForm()
    devices = {'DOOR': [], 'RELAY': [], 'READER': []}

    return render_template('settings/settings.html',
                           network_form=network_form,
                           security_form=security_form,
                           email_form=email_form,
                           rules_form=rules_form,
                           devices=devices)

