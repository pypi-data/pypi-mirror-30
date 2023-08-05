# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Unicode
from sqlalchemy.orm import relationship
from ..extensions import db


class HostSensors(db.Model):
    __tablename__ = 'host_sensors'

    idhost_sensors = Column(Integer, primary_key=True, nullable=True, autoincrement=True)
    name = Column(Unicode(45), nullable=True)
    location = Column(Unicode(45), nullable=False)
    host_idhost = Column(Integer, ForeignKey('host.idhost'))

    host_status = relationship('HostStatus', cascade='all, delete-orphan')
    mysql_engine = 'InnoDB'
