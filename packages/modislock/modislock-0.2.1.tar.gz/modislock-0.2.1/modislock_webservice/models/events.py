# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, TIMESTAMP, Enum
from sqlalchemy.sql import func
from ..extensions import db, marshmallow as ma


"""
@startuml
    !define table(x) class x << (T, #FFAAAA) >>
    !define primary_key(x) <u>x</u>

    table(Events){
        primary_key(id_event) INT
        event_time TIMESTAMP
        event_type ENUM(USER_CREATED, ACCESS, DENIED)
        user_id INT FK
        reader_settings_id_reader INT FK
    }
@enduml
"""


class Events(db.Model):
    __tablename__ = 'events'

    id_event = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    # TIMESTAMP Format on MySQL 1970-01-01 00:00:01
    event_time = Column(TIMESTAMP, default=func.now(), nullable=False)
    event_type = Column(Enum('USER_CREATED', 'ACCESS', 'DENIED'), nullable=False)
    # Foreign keys
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    reader_idreader = Column(Integer, ForeignKey('reader.idreader'))
    mysql_engine='InnoDB'


class EventsSchema(ma.Schema):
    class Meta:
        model = Events
        dateformat = '%Y-%m-%d %H:%M:%S'


