# coding: utf-8
from sqlalchemy import Column, ForeignKey, Unicode, DateTime
from ..extensions import db


class AppApiAccess(db.Model):

    __tablename__ = 'app_api_access'

    token = Column(Unicode(128), primary_key=True)
    expires = Column(DateTime)
    app_api_app_api_id = Column(db.Unicode(25), ForeignKey('app_api.app_api_id'), nullable=False)
    mysql_engine = 'InnoDB'
