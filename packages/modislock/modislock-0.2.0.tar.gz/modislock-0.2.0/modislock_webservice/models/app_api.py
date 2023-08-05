# coding: utf-8
from sqlalchemy import Column, Unicode
from sqlalchemy.orm import relationship
from ..extensions import db


class AppApi(db.Model):
    """Applications registered for API access

    """
    __tablename__ = 'app_api'

    app_api_id = Column(Unicode(25), primary_key=True)
    app_secret = Column(Unicode(128), nullable=False)
    app_api_access = relationship('AppApiAccess', cascade='all, delete-orphan')
    mysql_engine = 'InnoDB'

