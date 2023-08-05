# coding: utf-8
"""
    @startuml

    !define table(x) class x << (T, #FFAAAA) >>
    !define primary_key(x) <u>x</u>

    table(settings) {
        primary_key(id_settings) INT
        settings_name VARCHAR(45)
        units VARCHAR(45)
        settings_group_id_group INT
    }

    table(settings_group) {
        primary_key(id_group) INT
        name ENUM('WEB', 'READERS', 'MONITOR', 'RULES')
    }

    table(settings_values) {
        primary_key(id_values) INT
        value VARCHAR(45)
        settings_id_settings INT
    }

    SettingsGroup "1" *-- "many" Settings
    Settings "1" *-- "many" SettingsValues

    @enduml
"""
# coding: utf-8
from sqlalchemy import Column, Integer, Unicode, ForeignKey, Enum
from sqlalchemy.orm import relationship
from ..extensions import db, marshmallow as ma
from marshmallow import fields


class Settings(db.Model):

    __tablename__ = 'settings'

    settings_name = Column(Unicode(45), primary_key=True, unique=True, nullable=False)
    units = Column(Enum('STRING', 'INT', 'FLOAT', 'BOOL', 'TIME', 'DATE'))
    settings_value = Column(Unicode(128))
    # Foreign keys
    host_idhost = Column(Integer, ForeignKey('host.idhost'), nullable=False)
    mysql_engine = 'InnoDB'


class SettingsSchema(ma.Schema):
    class Meta:
        model = Settings

