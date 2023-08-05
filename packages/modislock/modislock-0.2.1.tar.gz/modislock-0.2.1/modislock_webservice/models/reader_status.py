# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.sql import func
from ..extensions import db, marshmallow as ma
from marshmallow import fields


class ReaderStatus(db.Model):
    __tablename__ = 'reader_status'

    id_status = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    timestamp = Column(TIMESTAMP, default=func.now(), nullable=False)
    temp = Column(Integer, nullable=False)
    validation_count = Column(Integer, nullable=False)
    denied_count = Column(Integer, nullable=False)
    reader_idreader = Column(Integer, ForeignKey('reader.idreader'))
    mysql_engine = 'MEMORY'


class ReaderStatusSchema(ma.Schema):
    id_status = fields.Int()
    timestamp = fields.DateTime()
    temp = fields.Int()
    validation_count = fields.Int()
    denied_count = fields.Int()
