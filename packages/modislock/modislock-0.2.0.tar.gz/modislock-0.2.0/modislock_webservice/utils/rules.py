
from ..extensions import db
from ..models import Settings
from sqlalchemy.exc import IntegrityError, InternalError, OperationalError


class RulesSettings:
    """
    glob_start = StringField(description='Start Access Time')
    glob_end = StringField(description="End Access Time")

    # Days of week
    glob_mon = BooleanField(description='Mon')
    glob_tue = BooleanField(description='Tue')
    glob_wed = BooleanField(description='Wed')
    glob_thr = BooleanField(description='Thr')
    glob_fri = BooleanField(description='Fri')
    glob_sat = BooleanField(description='Sat')
    glob_sun = BooleanField(description='Sun')
    """
    def __init__(self, form=None):
        if form is not None:
            for name in dir(form):
                if not name.startswith('_'):
                    unbound_field = getattr(form, name)
                    if hasattr(self, name):
                        setattr(self, name, unbound_field.data)

    @property
    def glob_start(self):
        start = Settings.query.filter(Settings.settings_name == 'GLOBAL_START_TIME').first()
        
        return '09:00:00' if start is None else start.settings_value
    
    @glob_start.setter
    def glob_start(self, start_time):
        start = Settings.query.filter(Settings.settings_name == 'GLOBAL_START_TIME').first()
        
        if start is not None:
            start.settings_value = start_time
            
            try:
                db.session.commit()
            except (IntegrityError, InternalError, OperationalError):
                db.session.rollback()

    @property
    def glob_end(self):
        end = Settings.query.filter(Settings.settings_name == 'GLOBAL_END_TIME').first()

        return '09:00:00' if end is None else end.settings_value

    @glob_end.setter
    def glob_end(self, end_time):
        end = Settings.query.filter(Settings.settings_name == 'GLOBAL_START_TIME').first()

        if end is not None:
            end.settings_value = end_time

            try:
                db.session.commit()
            except (IntegrityError, InternalError, OperationalError):
                db.session.rollback()
                
    @property
    def glob_mon(self):
        day = Settings.query.filter(Settings.settings_name == 'GLOBAL_DAYS').first()
        
        if day is not None:    
            day = int(day.settings_value) & 0x01
            return True if day else False
        else:
            return False
        
    @glob_mon.setter
    def glob_mon(self, enable):
        day = Settings.query.filter(Settings.settings_name == 'GLOBAL_DAYS').first()

        if day is not None:
            value = int(day.settings_value)
            if enable:
                value |= 0x01
            else:
                value &= ~0x01
            day.settings_value = str(value)
            
            try:
                db.session.commit()
            except (IntegrityError, InternalError, OperationalError):
                db.session.rollback()

    @property
    def glob_tue(self):
        day = Settings.query.filter(Settings.settings_name == 'GLOBAL_DAYS').first()

        if day is not None:
            day = int(day.settings_value) & 0x02
            return True if day else False
        else:
            return False

    @glob_tue.setter
    def glob_tue(self, enable):
        day = Settings.query.filter(Settings.settings_name == 'GLOBAL_DAYS').first()

        if day is not None:
            value = int(day.settings_value)
            if enable:
                value |= 0x02
            else:
                value &= ~0x02
            day.settings_value = str(value)

            try:
                db.session.commit()
            except (IntegrityError, InternalError, OperationalError):
                db.session.rollback()

    @property
    def glob_wed(self):
        day = Settings.query.filter(Settings.settings_name == 'GLOBAL_DAYS').first()

        if day is not None:
            day = int(day.settings_value) & 0x04
            return True if day else False
        else:
            return False

    @glob_wed.setter
    def glob_wed(self, enable):
        day = Settings.query.filter(Settings.settings_name == 'GLOBAL_DAYS').first()

        if day is not None:
            value = int(day.settings_value)
            if enable:
                value |= 0x04
            else:
                value &= ~0x04
            day.settings_value = str(value)

            try:
                db.session.commit()
            except (IntegrityError, InternalError, OperationalError):
                db.session.rollback()

    @property
    def glob_thr(self):
        day = Settings.query.filter(Settings.settings_name == 'GLOBAL_DAYS').first()

        if day is not None:
            day = int(day.settings_value) & 0x08
            return True if day else False
        else:
            return False

    @glob_thr.setter
    def glob_thr(self, enable):
        day = Settings.query.filter(Settings.settings_name == 'GLOBAL_DAYS').first()

        if day is not None:
            value = int(day.settings_value)
            if enable:
                value |= 0x08
            else:
                value &= ~0x08
            day.settings_value = str(value)

            try:
                db.session.commit()
            except (IntegrityError, InternalError, OperationalError):
                db.session.rollback()

    @property
    def glob_fri(self):
        day = Settings.query.filter(Settings.settings_name == 'GLOBAL_DAYS').first()

        if day is not None:
            day = int(day.settings_value) & 0x10
            return True if day else False
        else:
            return False

    @glob_fri.setter
    def glob_fri(self, enable):
        day = Settings.query.filter(Settings.settings_name == 'GLOBAL_DAYS').first()

        if day is not None:
            value = int(day.settings_value)
            if enable:
                value |= 0x10
            else:
                value &= ~0x10
            day.settings_value = str(value)

            try:
                db.session.commit()
            except (IntegrityError, InternalError, OperationalError):
                db.session.rollback()

    @property
    def glob_sat(self):
        day = Settings.query.filter(Settings.settings_name == 'GLOBAL_DAYS').first()

        if day is not None:
            day = int(day.settings_value) & 0x20
            return True if day else False
        else:
            return False

    @glob_sat.setter
    def glob_sat(self, enable):
        day = Settings.query.filter(Settings.settings_name == 'GLOBAL_DAYS').first()

        if day is not None:
            value = int(day.settings_value)
            if enable:
                value |= 0x20
            else:
                value &= ~0x20
            day.settings_value = str(value)

            try:
                db.session.commit()
            except (IntegrityError, InternalError, OperationalError):
                db.session.rollback()

    @property
    def glob_sun(self):
        day = Settings.query.filter(Settings.settings_name == 'GLOBAL_DAYS').first()

        if day is not None:
            day = int(day.settings_value) & 0x40
            return True if day else False
        else:
            return False

    @glob_sun.setter
    def glob_sun(self, enable):
        day = Settings.query.filter(Settings.settings_name == 'GLOBAL_DAYS').first()

        if day is not None:
            value = int(day.settings_value)
            if enable:
                value |= 0x40
            else:
                value &= ~0x40
            day.settings_value = str(value)

            try:
                db.session.commit()
            except (IntegrityError, InternalError, OperationalError):
                db.session.rollback()
