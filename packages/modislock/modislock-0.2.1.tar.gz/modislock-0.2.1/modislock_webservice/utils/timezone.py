
from flask import current_app
from ..extensions import db
from ..models import Settings
from sqlalchemy.exc import IntegrityError, InternalError, OperationalError

from datetime import datetime

from .sys_rtc import system_time, ntp_clock_sync, time_zone


class TimeZoneSettings:
    """
    sys_time = StringField(label='System Date/Time',
                       description='System Time',
                       validators=[DataRequired()])

    auto_time = BooleanField(label='Auto Time Sync',
                             description='Automatic Time Sync')

    tz_zone = SelectField
    """
    def __init__(self, form=None):
        if form is not None:
            for name in dir(form):
                if not name.startswith('_'):
                    unbound_field = getattr(form, name)
                    if hasattr(self, name):
                        setattr(self, name, unbound_field.data)

    @property
    def sys_time(self):
        return datetime.now().strftime('%H:%M:%S %Y-%m-%d')

    @sys_time.setter
    def sys_time(self, set_time):
        system_time(set_time)

    @property
    def auto_time(self):
        return ntp_clock_sync()

    @auto_time.setter
    def auto_time(self, enable):
        ntp_clock_sync(enable)

    @property
    def tz_zone(self):
        return time_zone()

    @tz_zone.setter
    def tz_zone(self, zone):
        time_zone(zone)