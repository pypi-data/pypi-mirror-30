# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Enum, Boolean
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from ..extensions import db, marshmallow as ma
from marshmallow import fields


class Relay(db.Model):
    __tablename__ = 'relay'

    idrelay = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    type = Column(Enum('SOLID_STATE', 'MECHANICAL'), nullable=False)
    enabled = Column(Boolean, nullable=False, default=False)
    position = Column(TINYINT, nullable=False)
    delay = Column(Integer, nullable=False, default=1500)
    controller_idcontroller = Column(Integer, ForeignKey('controller.idcontroller'), nullable=False)
    door_iddoor = Column(Integer, ForeignKey('door.iddoor'), nullable=False)
    door = relationship('Door')
    mysql_engine = 'InnoDB'


class RelaySchema(ma.Schema):
    idrelay = fields.Int()
    type = fields.Str()
    enabled = fields.Bool()
    position = fields.Int()
    delay = fields.Int()
    controller_idcontroller = fields.Int()
    door_iddoor = fields.Int()
    door = fields.Nested('DoorSchema')
