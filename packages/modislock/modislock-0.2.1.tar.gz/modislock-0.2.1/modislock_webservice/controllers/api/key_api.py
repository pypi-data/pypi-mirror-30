# coding: utf-8

# Flask and DB
from flask import current_app, jsonify
from flask_restful import (Resource, reqparse)
from sqlalchemy.sql.functions import count, coalesce
from sqlalchemy.exc import IntegrityError, InvalidRequestError

# Validators
from .decorators import app_required

# Database
from ...extensions import db
from ...models import (PinKey,
                       PinKeySchema,
                       RfidKey,
                       RfidKeySchema,
                       OtpKey,
                       OtpCloudService,
                       OtpKeySchema,
                       U2fKey,
                       U2fKeySchema,
                       TotpKey,
                       TotpKeySchema,
                       User,
                       Rules)

# Utils
from ...utils.key_generators import gen_unique_pin, gen_unique_webcode

# OTP
from yubiotp.otp import decode_otp, CRCError
from binascii import b2a_hex    # Bug in IntelliJ, will not recognise common modules

# U2F
# Keys
from u2flib_server.model import RegistrationData, websafe_decode


""" Dictionary of key types and associated data conversion scheme class """
proto_dict = {'pin': (PinKey, PinKeySchema), 'rfid': (RfidKey, RfidKeySchema),
              'otp': (OtpKey, OtpKeySchema), 'u2f': (U2fKey, U2fKeySchema),
              'totp': (TotpKey, TotpKeySchema)}

KEY_PROTOCOL = 0
KEY_SCHEMA = 1


class KeyAPI(Resource):
    """API management of key creation and modification

    Key enrollment for all protocols are possible through this API. U2F however, is quite challenging.
    In order to enroll a U2F key over the API, the key2 parameter needs to be obtained through another interface.
    This is due to the nature of U2F keys and how they sign their challenges.
    """

    decorators = [app_required]

    @staticmethod
    def _get_count(user_id):
        """
        
        .. code-block:: sql

            SELECT COALESCE(pin_count, 0) AS PIN, COALESCE(rfid_count, 0) AS RFID, COALESCE(otp_count, 0) AS OTP,
            COALESCE(totp_count, 0) as TOTP, COALESCE(u2f_count, 0) AS U2F, COALESCE(rules_count, 0) as RULES
            FROM user
            LEFT JOIN (SELECT user_id, COUNT(pin_key.key) as pin_count FROM pin_key GROUP BY user_id) as p ON p.user_id = user.id
            LEFT JOIN (SELECT user_id, COUNT(rfid_key.key) as rfid_count FROM rfid_key GROUP BY user_id) as r ON r.user_id = user.id
            LEFT JOIN (SELECT user_id, COUNT(otp_key.key) as otp_count FROM otp_key GROUP BY user_id) as o ON o.user_id = user.id
            LEFT JOIN (SELECT user_id, COUNT(totp_key.key) as totp_count FROM totp_key GROUP BY user_id) as t ON t.user_id = user.id
            LEFT JOIN (SELECT user_id, COUNT(u2f_key.key) as u2f_count FROM u2f_key GROUP BY user_id) as u ON u.user_id = user.id
            LEFT JOIN (SELECT user_id, COUNT(rules.days) as rules_count FROM rules GROUP BY user_id) as ru ON ru.user_id = user.id
            GROUP BY user.id;

        :param int user_id:
        :return dict: Dictionary of user pin type counts
        """
        pin_count = PinKey.query.with_entities(PinKey.user_id, count(PinKey.key).label('pin_count'))\
            .group_by(PinKey.user_id)\
            .subquery()
        rfid_count = RfidKey.query.with_entities(RfidKey.user_id, count(RfidKey.key).label('rfid_count'))\
            .group_by(RfidKey.user_id)\
            .subquery()
        otp_count = OtpKey.query.with_entities(OtpKey.user_id, count(OtpKey.key).label('otp_count'))\
            .group_by(OtpKey.user_id)\
            .subquery()
        totp_count = TotpKey.query.with_entities(TotpKey.user_id, count(TotpKey.key).label('totp_count'))\
            .group_by(TotpKey.user_id).subquery()
        u2f_count = U2fKey.query.with_entities(U2fKey.user_id, count(U2fKey.key).label('u2f_count'))\
            .group_by(U2fKey.user_id).subquery()
        rule_count = Rules.query.with_entities(Rules.user_id, count(Rules.days).label('rule_count'))\
            .group_by(Rules.user_id)\
            .subquery()

        key_count = User.query \
            .outerjoin(pin_count, pin_count.c.user_id == User.id) \
            .outerjoin(rfid_count, rfid_count.c.user_id == User.id) \
            .outerjoin(otp_count, otp_count.c.user_id == User.id) \
            .outerjoin(totp_count, totp_count.c.user_id == User.id) \
            .outerjoin(u2f_count, u2f_count.c.user_id == User.id) \
            .outerjoin(rule_count, rule_count.c.user_id == User.id) \
            .with_entities(coalesce(pin_count.c.pin_count, 0).label('PIN'),
                           coalesce(rfid_count.c.rfid_count, 0).label('RFID'),
                           coalesce(otp_count.c.otp_count, 0).label('OTP'),
                           coalesce(totp_count.c.totp_count, 0).label('TOTP'),
                           coalesce(u2f_count.c.u2f_count, 0).label('U2f'),
                           coalesce(rule_count.c.rule_count, 0).label('RULES')) \
            .filter(User.id == user_id) \
            .group_by(User.id) \
            .one_or_none()

        if key_count is not None:
            return [{'pin': key_count[0], 'rfid': key_count[1], 'otp': key_count[2], 'totp': key_count[3],
                    'u2f': key_count[4], 'rules': key_count[5]}]
        else:
            return [{'pin': 0, 'rfid': 0, 'otp': 0, 'totp': 0, 'u2f': 0, 'rules': 0}]

    def get(self, user_id):
        """GET KEY stuff

        .. http:get:: /api/v1.0/key/(int:user_id)?protocol=(string:protocol_type)

            A `user_id` and `protocol` is required.

            The protocol types available are:
                `pin` Simple PIN code
                `rfid` RFID code
                `otp` OTP code
                `u2f` U2F code
                `rules` User access rules
                `count` Count of types of keys available to the user

            **Example Request**

            .. sourcecode:: http

                GET /api/v1.0/key/1?protocol=pin HTTP/1.1
                Host: modislock.local
                Accept: application/json, text/javascript

            **Example Response**

            .. sourcecode:: http

                HTTP/1.1 200 OK
                Vary: Accept
                Content-Type: text/javascript

                {
                    "message": {
                        "key": {
                            "user_id": 1,
                            "enabled": true,
                            "created_on": "2017-10-10 13:15:05",
                            "key": 4444
                        },
                        "protocol": "pin"
                    }
                }

            :reqheader Authorization: X-APP-ID / X-APP-PASSWORD or X-APP-TOKEN (Password or Token generated by administration)

            :statuscode 200: No errors have occurred
            :statuscode 403: Credentials missing for api usage
        """
        parser = reqparse.RequestParser()
        parser.add_argument('protocol',
                            type=str,
                            required=True,
                            choices=('pin', 'rfid', 'otp', 'totp', 'u2f', 'count'),
                            help='Unrecognized protocol type: {error_msg}',
                            location='args')
        args = parser.parse_args()

        if args.protocol == 'count':
            return {'message': {'protocol': args.protocol,
                                'key': self._get_count(user_id),
                                'user_id': user_id}}

        table = proto_dict[args.protocol][KEY_PROTOCOL]
        table_schema = proto_dict[args.protocol][KEY_SCHEMA]()
        key = table.query.filter_by(user_id=user_id).one_or_none()

        return {'message': {'key': table_schema.dump(key).data,
                            'protocol': args.protocol}}

    def post(self, user_id):
        """API that adds a key to given user

        .. http:post:: /api/v1.0/key/(int:user_id)

            **Example Request**

            .. sourcecode:: http

                POST /api/v1.0/key/5
                Host: modislock.local
                Accept: application/json, text/javascript

            **Example Response**

            .. sourcecode:: http

                HTTP/1.1 200 OK
                Vary: Accept
                Content-Type: text/javascript

                {
                    "message": {
                        "success": "pin key added for user id 5",
                        "key": {
                            "created_on": "2017-11-02 14:07:44",
                            "user_id": 5,
                            "key": 7774,
                            "enabled": true
                        }
                    }
                }

            :param user_id: User ID number

            :formparam protocol: The protocol that will be enrolled (`pin`, `rfid`, `otp`, `totp`, `u2f`)
            :formparam key: If protocol dictates, a identification PIN code. This can also be generated from an API call to:
            :formparam key2: If protocol dictates, a second key. An example would be OTP which requires the AES code if the OTP key is to be locally validated.

            :reqheader Authorization: X-APP-ID / X-APP-PASSWORD or X-APP-TOKEN (Password or Token generated by administration)
            :reqheader Content-Type: application/x-www-form-urlencoded

            :statuscode 201: No errors have occurred and record was created
            :statuscode 403: Credentials missing for api usage
        """
        parser = reqparse.RequestParser()
        parser.add_argument('protocol',
                            type=str,
                            required=True,
                            choices=('pin', 'rfid', 'otp', 'totp', 'u2f'),
                            help='Unrecognized protocol type: {error_msg}',
                            location='form')

        user = User.query.filter_by(id=user_id).one_or_none()

        if user is None:
            return {'message': {'error': 'User id {} could not be found'.format(user_id)}}

        args = parser.parse_args()

        if args.protocol == 'pin':
            parser.add_argument('key',
                                type=int,
                                required=False,
                                help='Valid key',
                                location='form')
        elif args.protocol == 'rfid':
            parser.add_argument('key',
                                type=str,
                                required=True,
                                help='Valid key required',
                                location='form')
        elif args.protocol == 'otp':
            parser.add_argument('key',
                                type=str,
                                required=True,
                                help='Valid key required',
                                location='form')
            parser.add_argument('cloud',
                                type=bool,
                                required=True,
                                help='Cloud service used? True or False',
                                location='form')
            if parser.parse_args().cloud:
                parser.add_argument('cloud_usernane',
                                    type=str,
                                    required=False,
                                    help='Optional Yubico User ID',
                                    location='form')
                parser.add_argument('cloud_secret',
                                    type=str,
                                    required=False,
                                    help='Optional Yubico Secret Key',
                                    location='form')
            else:
                parser.add_argument('key2',
                                    type=str,
                                    required=True,
                                    help='Valid AES key required',
                                    location='form')
        elif args.protocol == 'totp':
            parser.add_argument('key',
                                type=int,
                                required=False,
                                help='Valid key 1st form of ID',
                                location='form')
            parser.add_argument('key2',
                                type=str,
                                required=False,
                                help='Generated random web key',
                                location='form')
        elif args.protocol == 'utf':
            parser.add_argument('key',
                                type=int,
                                required=False,
                                help='Challege presented to key',
                                location='form')
            parser.add_argument('key2',
                                type=str,
                                required=False,
                                help='Response from challenge',
                                location='form')
        args = parser.parse_args()

        key_class = proto_dict[args.protocol][KEY_PROTOCOL]
        key_scheme = proto_dict[args.protocol][KEY_SCHEMA]

        if args.protocol == 'pin':
            if args.key is None:
                args.key = gen_unique_pin()
            new_key = key_class(key=args.key, user_id=user_id)
            db.session.add(new_key)
        elif args.protocol == 'rfid':
            new_key = key_class(key=args.key, user_id=user_id)
            db.session.add(new_key)
        elif args.protocol == 'totp':
            if args.key is None:
                args.key = gen_unique_pin()
            if args.key2 is None:
                args.key2 = gen_unique_webcode()
            new_key = key_class(key=args.key, secret=args.key2, user_id=user_id)
            db.session.add(new_key)
        elif args.protocol == 'otp':
            if args.cloud is True:
                new_key = key_class(key=args.key[:12],
                                    private_identity=0,
                                    aeskey=0,
                                    counter=1,
                                    time=1,
                                    user_id=user_id,
                                    remote_server=True)
                db.session.add(new_key)
                cloud = OtpCloudService(yubico_user_name=args.cloud_usernane,
                                        yubico_secret_key=args.cloud_secret,
                                        otp_key_key=new_key.key)
                db.session.add(cloud)
            else:
                try:
                    public_id, otp_obj = decode_otp(bytes(args.key, encoding='utf-8'), bytes.fromhex(args.key2))
                except (CRCError, ValueError):
                    return jsonify({'error': 'AES Key Incorrect, validation failed'})

                new_key = key_class(key=public_id.decode('utf-8'),
                                    private_identity=b2a_hex(otp_obj.uid).decode('utf-8'),
                                    aeskey=args.key2,
                                    counter=otp_obj.counter,
                                    time=otp_obj.timestamp,
                                    user_id=user_id)
                db.session.add(new_key)
        elif args.protocol == 'u2f':
            reg_data = RegistrationData(websafe_decode(args.key2))
            new_key = key_class(key=args.key,
                                handle=reg_data.keyHandle,
                                public_key=reg_data.publicKey,
                                counter=1,
                                transports='USB',
                                user_id=user_id)
            db.session.add(new_key)

        try:
            db.session.commit()
        except (IntegrityError, InvalidRequestError) as e:
            db.session.rollback()
            current_app.logger.error('Unable to commit new key to database: {}'.format(e.orig.args[1]))
            return {'message': {'error': 'Key already exists'}}
        else:
            return {'message': {'success': '{} key added for user id {}'.format(args.protocol, user_id),
                                'key': key_scheme().dump(new_key).data}}, 201

    def put(self, user_id):
        """API to update the status of a given user and key

        .. http:put:: /api/v1.0/key/(int:user_id)

        **Example Request**

        .. sourcecode:: http

            PUT /api/v1.0/key/5
            Host: modislock.local
            Accept: application/json, text/javascript

        **Example Response**

        .. sourcecode:: http

            HTTP/1.1 201 OK
            Vary: Accept
            Content-Type: text/javascript

            {
                "message": {
                    "success": "Updated key for id 2 is now Enabled",
                    "key": {
                        "enabled": true,
                        "created_on": "2017-10-10 14:30:43",
                        "user_id": 2,
                        "key": 2492
                    }
                }
            }

        :param user_id: User ID number
        :formparam protocol: The protocol that will be enrolled (`pin`, `rfid`, `otp`, `totp`, `u2f`)
        :formparam enable: true / false

        :reqheader Authorization: X-APP-ID / X-APP-PASSWORD or X-APP-TOKEN (Password or Token generated by administration)
        :reqheader Content-Type: application/x-www-form-urlencoded

        :statuscode 201: No errors have occurred and record was updated
        :statuscode 403: Credentials missing for api usage

        """
        parser = reqparse.RequestParser()
        parser.add_argument('protocol',
                            type=str,
                            required=True,
                            choices=('pin', 'rfid', 'otp', 'totp', 'u2f'),
                            help='Unrecognized protocol type: {error_msg}',
                            location='form')
        parser.add_argument('enable',
                            type=bool,
                            required=True,
                            help='Enabled or disabled [true / false]',
                            location='form')

        args = parser.parse_args()

        key_class = proto_dict[args.protocol][KEY_PROTOCOL]
        key_schema = proto_dict[args.protocol][KEY_SCHEMA]
        key_code = key_class.query.filter_by(user_id=user_id).one_or_none()

        if key_code is None:
            return {'message': {'error': 'User id {} does not have a {} key'.format(user_id, args.protocol)}}

        key_code.enabled = args.enable

        try:
            db.session.commit()
        except (IntegrityError, InvalidRequestError) as e:
            db.session.rollback()
            current_app.logger.error('Error committing to database: {}'.format(e.args[0]))

            return {'message': {'error': 'ERROR COMMITTING TO DATABASE'}}

        return {'message': {'success': 'Updated key for id {} is now {}'.format(user_id, 'Enabled' if args.enable else 'Disabled'),
                            'key': key_schema().dump(key_code).data}}, 201

    def delete(self, user_id):
        """Deletes a users key

        .. http:delete:: /api/v1.0/key/(int:user_id)?protocol=(string:protocol_type)

         **Example Request**

        .. sourcecode:: http

            DELETE /api/v1.0/key/301?protocol=pin
            Host: modislock.local
            Accept: application/json, text/javascript

        **Example Response**

        .. sourcecode:: http

            HTTP/1.1 204 OK
            Vary: Accept
            Content-Type: text/javascript

        :param user_id: User ID number

        :reqheader Authorization: X-APP-ID / X-APP-PASSWORD or X-APP-TOKEN (Password or Token generated by administration)

        :statuscode 204: No errors have occurred and record was created
        :statuscode 403: Credentials missing for api usage
        """
        parser = reqparse.RequestParser()
        parser.add_argument('protocol',
                            type=str,
                            required=True,
                            choices=('pin', 'rfid', 'otp', 'totp', 'u2f'),
                            help='Unrecognized protocol type: {error_msg}',
                            location='args')
        args = parser.parse_args()

        key_class = proto_dict[args.protocol][KEY_PROTOCOL]

        del_key = key_class.query.filter_by(user_id=user_id).one_or_none()

        if del_key is None:
            return {'message': {'error': 'User id {} not found'.format(user_id)}}

        db.session.delete(del_key)

        try:
            db.session.commit()
        except (IntegrityError, InvalidRequestError) as e:
            db.session.rollback()
            current_app.logger.error('Could not delete from database: ' + e.args[0])
            return {'message': {'error': 'Could not delete from database'}}
        else:
            return {}, 204
