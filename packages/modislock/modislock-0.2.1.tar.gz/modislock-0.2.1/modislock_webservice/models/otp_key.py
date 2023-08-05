# coding: utf-8
from ..extensions import db, marshmallow as ma
from sqlalchemy.sql import func

"""
@startuml
!define table(x) class x << (T, #FFAAAA) >>
!define primary_key(x) <u>x</u>

table(OtpKey){
    primary_key(key) VARCHAR(16)
    private_identity VARCHAR(16)
    aeskey VARCHAR(32)
    enabled BOOLEAN
    counter INT(11)
    time INT
    created_on TIMESTAMP
    remote_server BOOLEAN
    user_id INT
}
@enduml
"""


class OtpKey(db.Model):
    __tablename__ = 'otp_key'

    key = db.Column(db.Unicode(16), primary_key=True, nullable=False, index=True)
    private_identity = db.Column(db.Unicode(16), nullable=False)
    aeskey = db.Column(db.Unicode(32), nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, default=1)
    counter = db.Column(db.Integer, nullable=False, default=1)
    time = db.Column(db.Integer, nullable=False, default=1)
    nonce = db.Column(db.Unicode(45))
    created_on = db.Column(db.TIMESTAMP, default=func.now(), nullable=False)
    remote_server = db.Column(db.Boolean, default=0)
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    otp_cloud_service = db.relationship('OtpCloudService', cascade='all, delete-orphan')
    mysql_engine = 'InnoDB'


class OtpCloudService(db.Model):
    __tablename__ = 'otp_cloud_service'
    cloud_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    yubico_user_name = db.Column(db.Unicode(45), nullable=True)
    yubico_secret_key = db.Column(db.Unicode(45), nullable=True)
    # Foreign keys
    otp_key_key = db.Column(db.Unicode(16), db.ForeignKey('otp_key.key'), nullable=False)
    mysql_engine = 'InnoDB'


class OtpKeySchema(ma.Schema):
    class Meta:
        model = OtpKey
        dateformat = '%Y-%m-%d %H:%M:%S'
        fields = ('key', 'private_identity', 'aeskey', 'enabled', 'created_on', 'remote_server', 'user_id')

