# coding: utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, InputRequired, NumberRange, ValidationError


class SettingsGlobalTimeForm(FlaskForm):
    """Global access time rules

    """
    glob_start = StringField(description='Start Access Time')
    glob_end = StringField(description="End Access Time")

    # Days of week
    glob_mon = BooleanField(description='Mon')
    glob_tue = BooleanField(description='Tue')
    glob_wed = BooleanField(description='Wed')
    glob_thr = BooleanField(description='Thr')
    glob_fri = BooleanField(description='Fri')
    glob_sat = BooleanField(description='Sat')
    glob_sun = BooleanField(description='Sun')

    # Submit to save
    submit_rules_btn = SubmitField('Save Rules')

