# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.sql import func
from ..extensions import db, marshmallow as ma
from marshmallow import fields


class ControllerStatus(db.Model):
    __tablename__ = 'controller_status'

    idcontroller_status = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    timestamp = Column(TIMESTAMP, nullable=False, default=func.now())
    temp = Column(Integer, nullable=False, default=0)
    validation_count = Column(Integer, nullable=False, default=0)
    denied_count = Column(Integer, nullable=False, default=0)
    controller_idcontroller = Column(Integer, ForeignKey('controller.idcontroller'), nullable=False)
    mysql_engine = 'MEMORY'


class ControllerStatusSchema(ma.Schema):
    idcontroller_status = fields.Int()
    timestamp = fields.DateTime()
    temp = fields.Int()
    validation_count = fields.Int()
    denied_count = fields.Int()
    controller_idcontroller = fields.Int()