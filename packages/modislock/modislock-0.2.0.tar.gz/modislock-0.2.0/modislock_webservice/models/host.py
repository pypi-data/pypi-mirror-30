# coding: utf-8
from sqlalchemy import Column, Integer, Unicode, Boolean, DATE
from sqlalchemy.orm import relationship
from ..extensions import db


class Host(db.Model):
    __tablename__ = 'host'

    idhost = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    serial_number = Column(Unicode(45), nullable=False)
    host_name = Column(Unicode(45), nullable=False)
    installation_date = Column(DATE, nullable=False)
    registered = Column(Boolean, nullable=False)

    controller = relationship('Controller', cascade='all, delete-orphan')
    host_sensors = relationship('HostSensors', cascade='all, delete-orphan')
    settings = relationship('Settings', cascade='all, delete-orphan')
    mysql_engine = 'InnoDB'
