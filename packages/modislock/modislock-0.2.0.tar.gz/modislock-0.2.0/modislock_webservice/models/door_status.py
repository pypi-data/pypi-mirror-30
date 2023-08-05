# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Enum, TIMESTAMP
from sqlalchemy.sql import func
from ..extensions import db, marshmallow as ma


class DoorStatus(db.Model):
    __tablename__ = 'door_status'

    iddoor_status = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    status = Column(Enum('ACTIVE', 'INACTIVE'), nullable=False, default='INACTIVE')
    timestamp = Column(TIMESTAMP, nullable=False, default=func.now())
    door_iddoor = Column(Integer, ForeignKey('door.iddoor'), nullable=False)
    mysql_engine = 'MEMORY'


class DoorStatusSchema(ma.Schema):
    class Meta:
        model = DoorStatus
