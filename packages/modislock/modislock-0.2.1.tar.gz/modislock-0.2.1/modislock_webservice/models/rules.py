# coding: utf-8
from ..extensions import db
from sqlalchemy.dialects.mysql import TINYINT

"""
@startuml
!define table(x) class x << (T, #FFAAAA) >>
!define primary_key(x) <u>x</u>

table(rules){
    primary_key(id_rules) INT
    days TINYINT
    start_time TIME
    end_time TIME
    readers TINY
    user_id INT
}
@enduml
"""


class Rules(db.Model):
    __tablename__ = 'rules'

    id_rules = db.Column(db.Integer, primary_key=True, autoincrement=True)
    days = db.Column(TINYINT(unsigned=True))
    start_time = db.Column(db.TIME)
    end_time = db.Column(db.TIME)
    readers = db.Column(TINYINT(unsigned=True))
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mysql_engine = 'InnoDB'


__all__ = ['Rules']
