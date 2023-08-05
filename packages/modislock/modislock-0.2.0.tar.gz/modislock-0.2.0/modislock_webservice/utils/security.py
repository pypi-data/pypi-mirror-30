from flask import current_app
from ..extensions import db
from ..models import Settings
from sqlalchemy.exc import InternalError, IntegrityError


class SecuritySettings:

    def __init__(self, form=None):
        if form is not None:
            for name in dir(form):
                if not name.startswith('_'):
                    unbound_field = getattr(form, name)
                    if hasattr(self, name):
                        setattr(self, name, unbound_field.data)

    @property
    def pin_places(self):
        pin = Settings.query.filter(Settings.settings_name == 'PIN_PLACES').first()

        if pin is not None:
            return int(pin.settings_value)
        else:
            return 4

    @pin_places.setter
    def pin_places(self, places):
        pin = Settings.query.filter(Settings.settings_name == 'PIN_PLACES').first()

        if pin is not None:
            pin.settings_value = str(places)

            try:
                db.session.commit()
            except (IntegrityError, InternalError) as e:
                db.session.rollback()

    @property
    def months_preserved(self):
        months = Settings.query.filter(Settings.settings_name == 'MONTHS_PRESERVED').first()

        if months is not None:
            return int(months.settings_value)
        else:
            return 1

    @months_preserved.setter
    def months_preserved(self, months):
        saved = Settings.query.filter(Settings.settings_name == 'MONTHS_PRESERVED').first()

        if saved is not None:
            saved.settings_value = str(months)

            try:
                db.session.commit()
            except (IntegrityError, InternalError) as e:
                db.session.rollback()

    @property
    def ssh_access(self):
        ssh = Settings.query.filter(Settings.settings_name == 'OPTION_SSH_ENABLE').first()

        if ssh is not None:
            return True if ssh.settings_value == 'True' else False
        else:
            return False

    @ssh_access.setter
    def ssh_access(self, enabled):
        ssh = Settings.query.filter(Settings.settings_name == 'OPTION_SSH_ENABLE').first()

        if ssh is not None:
            ssh.settings_value = 'True' if enabled else 'False'

            try:
                db.session.commit()
            except (IntegrityError, InternalError) as e:
                db.session.rollback()
