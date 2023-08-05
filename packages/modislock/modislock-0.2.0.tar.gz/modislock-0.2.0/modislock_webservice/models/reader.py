# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Unicode, Enum, Date, Boolean
from sqlalchemy.orm import relationship
from ..extensions import db, marshmallow as ma
from marshmallow import fields


class Reader(db.Model):
    __tablename__ = 'reader'

    idreader = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(Unicode(45), nullable=False)
    status = Column(Enum('ACTIVE', 'INACTIVE'), nullable=False)
    enabled = Column(Boolean, nullable=False)
    pin_num = Column(Integer, nullable=False, default=0)
    alt_name = Column(Unicode(45))
    location = Column(Unicode(45))
    location_direction = Column(Enum('ENTRY', 'EXIT'))
    uuid = Column(Unicode(45))
    software_version = Column(Unicode(10))
    service_date = Column(Date)
    validation_count = Column(Integer)
    denied_count = Column(Integer)
    controller_address = Column(Integer, nullable=False)

    controller_idcontroller = Column(Integer,
                                     ForeignKey('controller.idcontroller'),
                                     nullable=False)
    door_iddoor = Column(Integer, ForeignKey('door.iddoor'), nullable=False)

    events = relationship('Events', cascade='all, delete-orphan')
    reader_status = relationship('ReaderStatus', cascade='all, delete-orphan')
    mysql_engine = 'InnoDB'


class ReaderSchema(ma.Schema):
    idreader = fields.Int()
    name = fields.Str()
    status = fields.Str()
    enabled = fields.Boolean()
    pin_num = fields.Int()
    alt_name = fields.Str()
    location = fields.Str()
    location_direction = fields.Str()
    uuid = fields.Str()
    software_version = fields.Float()
    service_date = fields.Date()
    validation_count = fields.Int()
    denied_count = fields.Int()
    controller_address = fields.Int()
    door_iddoor = fields.Int()
    events = fields.Nested('EventsSchema', many=True)
    reader_status = fields.Nested('ReaderStatusSchema', many=True)
