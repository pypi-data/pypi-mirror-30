# coding: utf-8
from ..extensions import db, marshmallow as ma
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.sql import func

"""
@startuml
!define table(x) class x << (T, #FFAAAA) >>
!define primary_key(x) <u>x</u>

table(TotpKey){
    primary_key(key) INT
    secret VARCHAR(16)
    period TINY INT
    enabled BOOLEAN
    created_on TIMESTAMP
    user_id INT
}
@enduml
"""


class TotpKey(db.Model):
    __tablename__ = 'totp_key'

    key = db.Column(db.Integer, primary_key=True, unique=True)
    secret = db.Column(db.Unicode(40))
    period = db.Column(TINYINT, nullable=False, default=30)
    enabled = db.Column(db.Boolean, default=1)
    created_on = db.Column(db.TIMESTAMP, default=func.now(), nullable=False)
    nonce = db.Column(db.Unicode(45))
    time = db.Column(db.Integer)
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mysql_engine = 'InnoDB'


class TotpKeySchema(ma.Schema):
    class Meta:
        model = TotpKey
        dateformat = '%Y-%m-%d %H:%M:%S'
        fields = ('key', 'secret', 'period', 'enabled', 'created_on', 'user_id')


__all__ = ['TotpKey', 'TotpKeySchema']
