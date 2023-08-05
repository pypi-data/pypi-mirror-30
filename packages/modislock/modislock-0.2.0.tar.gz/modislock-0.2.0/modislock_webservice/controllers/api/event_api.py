# coding: utf-8

# Flask and DB
from flask_restful import Resource, reqparse
from sqlalchemy.sql.expression import or_, and_

# Validators
from .decorators import app_required

# Database
from ...extensions import marshmallow as ma
from ...models import (Events, Reader, User)
from marshmallow import fields
from datetime import datetime


parser = reqparse.RequestParser()
parser.add_argument('start_time',
                    type=str,
                    required=True,
                    location='args',
                    help='A valid start time is required: ex 2017-05-25 12:12:00')
parser.add_argument('end_time',
                    type=str,
                    required=True,
                    location='args',
                    help='A valid end time is required: ex 2017-05-25 12:12:00')
parser.add_argument('event_type',
                    type=str,
                    required=True,
                    location='args',
                    choices=('A', 'B', 'D'),
                    help='A=accesses, B=both accesses and denied, D=denied')


class EventAPI(Resource):
    """API Call that queries access and denied events from the logs

    """
    decorators = [app_required]

    @staticmethod
    def _validate_date(date_text):
        """Validate that provided date is within acceptable parameters and is in fact a date

        """
        result = True

        try:
            datetime.strptime(date_text, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            result = False

        return result

    def get(self, user_id):
        """Retrieve access events from logs

        .. http:get:: /api/v1.0/event/(int:user_id)?(datetime:start_time)&(datetime:end_time)&(string:event_type)

            **Example Missing Parameter Request**

            .. sourcecode:: http

                GET /api/v1.0/event/0?start_time=2017-05-06 12:00:00&event_type=A
                Host: modislock.local
                Accept: application/json, text/javascript

            **Example Response**

            .. sourcecode:: http

                HTTP/1.1 200 OK
                Vary: Accept
                Content-type: text/javascript

                {
                    "message": {
                        "end_time": "A valid end time is required: ex 2017-05-25 12:12:00"
                    }
                }

            **Example Successful Request**

            .. sourcecode:: http

                GET /api/v1.0/event/12?start_time=2017-05-06 12:00:00&end_time=2017-08-08 12:00:00&event_type=A
                Host: modislock.local
                Accept: application/json, text/javascript

            **Example Response**

            .. sourcecode:: http

                HTTP/1.1 200 OK
                Vary: Accept
                Content-Type: text/javascript

                {
                    "message": {
                        "user": 12,
                        "events": [
                            {
                                "event_type": "ACCESS",
                                "location_name": "READER 1",
                                "id_event": 8450,
                                "event_time": "2017-07-11 00:06:45",
                                "user_id": 12,
                                "location_direction": "ENTRY"
                            },
                            {
                                "event_type": "ACCESS",
                                "location_name": "READER 3",
                                "id_event": 14485,
                                "event_time": "2017-07-18 18:13:30",
                                "user_id": 12,
                                "location_direction": "ENTRY"
                            },
                            {
                                "event_type": "ACCESS",
                                "location_name": "READER 4",
                                "id_event": 14794,
                                "event_time": "2017-05-25 20:39:06",
                                "user_id": 12,
                                "location_direction": "EXIT"
                            }
                        ],
                        "count": 3
                    }
                }

            :param int user_id: Users ID number
            :param datetime start_time: Start of date and time to search
            :param datatime end_time: End of date and time where to search
            :param str event_type: Type of events to search

            .. warning:: When a field is not provided (`start_time`, `end_time`, `event_type`), a help message will be returned

            .. note:: To query a specific user, their `user_id` number is required.

            .. note:: To query for all records of **all** users, user id should be 0.

            .. note:: Accepted Event types are:

                - A Access Events
                - B Both Access and Denied
                - D Denied Events

            :query sort: ``event_time``
            :query limit: No limit
            :reqheader Authorization: X-APP-ID / X-APP-PASSWORD or X-APP-TOKEN (Password or Token generated by administration)
            :statuscode 200: No errors have occurred
            :statuscode 403: Credentials missing for api usage
        """
        args = parser.parse_args()

        start_time = None if self._validate_date(args.start_time) is False else args.start_time
        end_time = None if self._validate_date(args.end_time) is False else args.end_time

        if start_time is None or end_time is None:
            return {'message': {'error': 'Improper date format specified'}}

        filters = [
            Events.event_time > start_time,
            Events.event_time < end_time
        ]

        if args.event_type is 'D':
            filters.append(Events.event_type == 'DENIED')
        elif args.event_type is 'B':
            filters.append(or_(Events.event_type == 'ACCESS', Events.event_type == 'DENIED'))
        else:
            filters.append(Events.event_type == 'ACCESS')

        # User is present
        if user_id != 0:
            filters.append(User.id == user_id)

        filters.append(Events.reader_settings_id_reader != 0)

        events = Events.query \
            .join(Reader, Reader.id_reader == Events.reader_settings_id_reader) \
            .join(User, User.id == Events.user_id) \
            .filter(and_(*filters)) \
            .with_entities(Events.id_event,
                           Events.user_id,
                           Events.event_time,
                           Events.event_type,
                           Reader.location_name,
                           Reader.location_direction)\
            .all()

        class EventAPISchema(ma.Schema):
            id_event = fields.Integer()
            user_id = fields.Integer()
            event_time = fields.DateTime(format='%Y-%m-%d %H:%M:%S')
            event_type = fields.String()
            location_name = fields.String()
            location_direction = fields.String()

        return {'message': {'user': user_id,
                            'events': EventAPISchema(many=True).dump(events).data,
                            'count': len(events)}}
