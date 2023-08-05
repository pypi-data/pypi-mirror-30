# coding: utf-8
from sqlalchemy import Column, Integer
from ..extensions import db


class Recent24hApprovedHourly(db.Model):
    __tablename__ = "recent_24h_approved_hourly"

    H0 = Column(Integer, primary_key=True)
    H1 = Column(Integer)
    H2 = Column(Integer)
    H3 = Column(Integer)
    H4 = Column(Integer)
    H5 = Column(Integer)
    H6 = Column(Integer)
    H7 = Column(Integer)
    H8 = Column(Integer)
    H9 = Column(Integer)
    H10 = Column(Integer)
    H11 = Column(Integer)
    H12 = Column(Integer)
    H13 = Column(Integer)
    H14 = Column(Integer)
    H15 = Column(Integer)
    H16 = Column(Integer)
    H17 = Column(Integer)
    H18 = Column(Integer)
    H19 = Column(Integer)
    H20 = Column(Integer)
    H21 = Column(Integer)
    H22 = Column(Integer)
    H23 = Column(Integer)
