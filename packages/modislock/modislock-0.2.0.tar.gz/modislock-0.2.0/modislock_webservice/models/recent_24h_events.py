# coding: utf-8
from sqlalchemy import Column, Enum, Unicode, Integer
from sqlalchemy.dialects.mysql import TIMESTAMP
from ..extensions import db, marshmallow as ma


class Recent24hEvents(db.Model):
    __tablename__ = 'recent_24h_events'

    id_event = Column(Integer, nullable=False, primary_key=True)
    id = Column(Integer)
    first_name = Column(Unicode(50))
    last_name = Column(Unicode(50))
    event_type = Column(Enum('USER_CREATED', 'ACCESS', 'DENIED'))
    event_time = Column(TIMESTAMP)
    location = Column(Unicode(45))
    location_direction = Column(Unicode(45))


class Recent24hEventsSchema(ma.Schema):
    class Meta:
        model = Recent24hEvents
        fields = ('id_event', 'id', 'first_name', 'last_name', 'event_type', 'event_time', 'location', 'location_direction')
