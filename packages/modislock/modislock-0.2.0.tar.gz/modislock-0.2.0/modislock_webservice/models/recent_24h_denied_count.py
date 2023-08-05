# coding: utf-8
from sqlalchemy import Column, Integer
from ..extensions import db


class Recent24hDeniedCount(db.Model):
    __tablename__ = "recent_24h_denied_count"

    denied_count = Column(Integer, nullable=False, default=0, primary_key=True)

