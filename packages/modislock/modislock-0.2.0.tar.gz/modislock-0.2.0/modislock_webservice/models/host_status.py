# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.sql import func
from ..extensions import db


class HostStatus(db.Model):
    __tablename__ = 'host_status'

    idhost_status = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    reading = Column(Integer, nullable=False)
    timestamp = Column(TIMESTAMP, default=func.now(), nullable=False)
    host_sensors_idhost_sensors = Column(Integer, ForeignKey('host_sensors.idhost_sensors'))
    mysql_engine = 'MEMORY'

