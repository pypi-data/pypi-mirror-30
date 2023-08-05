# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Unicode, Date
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from ..extensions import db, marshmallow as ma
from marshmallow import fields


class Controller(db.Model):
    """Controller represents a device connected to a host and is connected to readers, doors, and relays

    """
    __tablename__ = 'controller'

    idcontroller = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    uuid = Column(Unicode(45))
    software_version = Column(Unicode(10))
    service_date = Column(Date)
    name = Column(Unicode(45), nullable=False)
    port = Column(Unicode(45), nullable=False)
    baud_rate = Column(Integer, nullable=False, default=115200)
    data_bits = Column(TINYINT, nullable=False, default=8)
    stop_bits = Column(TINYINT, nullable=False, default=1)
    host_idhost = Column(Integer, ForeignKey('host.idhost'), nullable=False)

    reader = relationship('Reader', cascade='all, delete-orphan')
    door = relationship('Door', cascade='all, delete-orphan')
    relay = relationship('Relay', cascade='all, delete-orphan')
    controller_status = relationship('ControllerStatus', cascade='all, delete-orphan')
    mysql_engine = 'InnoDB'


class ControllerSchema(ma.Schema):
    idcontroller = fields.Integer()
    uuid = fields.Str()
    software_version = fields.Str()
    service_date = fields.Date()
    name = fields.Str()
    reader = fields.Nested('ReaderSchema',
                           many=True,
                           only=('idreader',
                                 'name',
                                 'status',
                                 'enabled',
                                 'alt_name',
                                 'location',
                                 'location_direction',
                                 'uuid',
                                 'software_version',
                                 'service_date',
                                 'validation_count',
                                 'denied_count',
                                 'door_iddoor'))
    door = fields.Nested('DoorSchema',
                         many=True,
                         only=('iddoor',
                               'name',
                               'alt_name',
                               'door_status'))
    relay = fields.Nested('RelaySchema',
                          many=True,
                          only=('idrelay',
                                'type',
                                'enabled',
                                'position',
                                'delay',
                                'door_iddoor'))
    controller_status = fields.Nested('ControllerStatusSchema', many=True)
