# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Unicode
from sqlalchemy.orm import relationship
from ..extensions import db, marshmallow as ma
from marshmallow import fields


class Door(db.Model):
    __tablename__ = 'door'

    iddoor = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(Unicode(45), nullable=False)
    pin_num = Column(Integer, nullable=False)
    alt_name = Column(Unicode(45))
    controller_idcontroller = Column(Integer, ForeignKey('controller.idcontroller'))

    door_status = relationship('DoorStatus', cascade='all, delete-orphan')
    reader = relationship('Reader')
    relay = relationship('Relay')
    mysql_engine = 'InnoDB'


class DoorSchema(ma.Schema):
    iddoor = fields.Int()
    name = fields.Str()
    pin_num = fields.Int()
    alt_name = fields.Str()
    controller_idcontroller = fields.Int()
    door_status = fields.Nested('DoorStatusSchema')
    reader = fields.Nested('ReaderSchema', many=True)
    relay = fields.Nested('RelaySchema', many=True)
