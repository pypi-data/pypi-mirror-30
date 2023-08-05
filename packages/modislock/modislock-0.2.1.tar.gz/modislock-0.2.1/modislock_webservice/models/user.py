# coding: utf-8

from ..extensions import db, marshmallow as ma
from sqlalchemy.ext.hybrid import hybrid_property
from flask_security.utils import hash_password, verify_password
from marshmallow import fields

"""
@startuml
!define table(x) class x << (T, #FFAAAA) >>
!define primary_key(x) <u>x</u>

table(User){
    primary_key(id) INT
    first_name VARCHAR(50)
    last_name VARCHAR(50)
    email VARCHAR(50)
    password VARCHAR(128)
    is_admin BOOLEAN
}
@enduml
"""


class User(db.Model):
    """
    User table defines login information but is also referenced in all available protocols
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Unicode(45))
    first_name = db.Column(db.Unicode(50), nullable=False)
    last_name = db.Column(db.Unicode(50), nullable=False)
    email = db.Column(db.Unicode(50), unique=True)
    password = db.Column(db.Unicode(128))
    is_admin = db.Column(db.Boolean, nullable=False, default=0)

    # Relationships
    events = db.relationship('Events', cascade='all, delete-orphan')
    rules = db.relationship('Rules', cascade='all, delete-orphan')
    pin_key = db.relationship('PinKey', cascade='all, delete-orphan')
    rfid_key = db.relationship('RfidKey', cascade='all, delete-orphan')
    totp_key = db.relationship('TotpKey', cascade='all, delete-orphan')
    otp_key = db.relationship('OtpKey', cascade='all, delete-orphan')
    u2f_key = db.relationship('U2fKey', cascade='all, delete-orphan')
    mysql_engine = 'InnoDB'

    def check_password(self, password):
        return verify_password(password, self.password)

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id

    def is_active(self):
        """True, as all users are active."""
        return True

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    @hybrid_property
    def roles(self):
        """Added as per https://github.com/mattupstate/flask-security/issues/188
        Does not have a roles table or reference
        :return:
        """
        return []

    @roles.setter
    def roles(self, role):
        pass


class UserSchema(ma.Schema):
    id = fields.Integer()
    uid = fields.Str()
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Str()
    events = fields.Nested('EventsSchema', only=['event_type', 'event_time', 'reader_idreader'], many=True)
    pin_key = fields.Nested('PinKeySchema', only=['key', 'enabled', 'created_on'], many=True)
    rfid_key = fields.Nested('RfidKeySchema', only=['key', 'enabled', 'created_on'], many=True)
    otp_key = fields.Nested('OtpKeySchema', only=['key', 'enabled', 'created_on', 'remote_server'], many=True)
    totp_key = fields.Nested('TotpKeySchema', only=['key', 'enabled', 'created_on'], many=True)
    u2f_key = fields.Nested('U2fKeySchema', only=['key', 'enabled', 'created_on'], many=True)


class LDAPUsersSchema(ma.Schema):
    uid = fields.Str()
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Str()