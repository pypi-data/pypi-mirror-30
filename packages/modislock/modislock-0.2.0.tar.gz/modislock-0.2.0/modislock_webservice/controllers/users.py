# coding: utf-8

# Flask
from flask import render_template, Blueprint, request, jsonify, abort, current_app
from flask_security import login_required
from flask_security.utils import hash_password

# Database
from ..models import (PinKey,
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
                      Settings,
                      LDAPUsersSchema,
                      Events,
                      Rules)
from ..extensions import marshmallow as ma, db, cache
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.functions import count, coalesce
from sqlalchemy.exc import IntegrityError, InternalError, InvalidRequestError
from marshmallow import fields

# Keys
from u2flib_server.model import RegistrationData, websafe_decode, websafe_encode

# OTP
from pyotp import TOTP
from yubiotp.otp import decode_otp, CRCError
from binascii import b2a_hex    # Bug in IntelliJ, will not recognise common modules

# Email notifications
import pyqrcode
from io import BytesIO
import base64
from ..utils.mail_utils import send_email
from ..utils.key_generators import gen_unique_pin
from ..utils.ldap import ldap_get_users

# Misc
from collections import defaultdict
import io
import os


""" Dictionary of key types and associated data conversion scheme class """
proto_dict = {'pin': (PinKey, PinKeySchema), 'rfid': (RfidKey, RfidKeySchema),
              'otp': (OtpKey, OtpKeySchema), 'u2f': (U2fKey, U2fKeySchema),
              'totp': (TotpKey, TotpKeySchema)}

KEY_PROTOCOL = 0
KEY_SCHEMA = 1

bp = Blueprint('users', __name__)


def _get_app_id():
    """Retrieve application ID for U2F signing

    :returns str app_id: Application ID
    """
    return current_app.config.get('SITE_DOMAIN')


def _get_request_data(form):
    """Converts SQLAlchemy query to dictionary

    return dict list with data from request.form
    request.form comes in multidict [('data[id][field]',value), ...]
    :param form: MultiDict from `request.form`
    :rtype: {id1: {field1:val1, ...}, ...} [field(n) and val(n) are strings]
    """
    # fill in id field automatically
    data = defaultdict(lambda: {})

    # fill in data[id][field] = value
    for form_key in form.keys():
        if form_key == 'action':
            continue
        data_part, id_part, field_part = form_key.split('[')

        if data_part != 'data':
            raise ValueError("invalid input in request: {}".format(form_key))

        id_value = int(id_part[0:-1])
        field_name = field_part[0:-1]
        data[id_value][field_name] = form[form_key]
    return data  # return decoded result


@bp.route('/users/users', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def user_access():
    """Manages all users on system, allows for reading, deleting, adding or updating of users.

    Methods accepted are GET, POST, PUT, DELETE

    :return: User Data

    :rtype: GET Request returns { data :[id: (int), first_name: (str), last_name: (str), email: (str), is_admin: (bool), last_active:(datetime) ]}

            POST Request returns single user  { data :[id: (int), first_name: (str), last_name: (str), email: (str), is_admin: (bool), last_active:(datetime) ]}

            PUT Request returns single user  { data :[id: (int), first_name: (str), last_name: (str), email: (str), is_admin: (bool), last_active:(datetime) ]}

            DELETE Request returns empty dict on success {}

            Errors are returned as {'error': 'message'}

    """
    class UsersSchema(ma.Schema):
        id = fields.Integer()
        first_name = fields.String()
        last_name = fields.String()
        email = fields.Email()
        is_admin = fields.Boolean()
        last_active = fields.DateTime(format='%Y-%m-%d %H:%M:%S')

    if request.method == 'GET':
        sub_query = Events.query.with_entities(Events.user_id, func.max(Events.event_time).label('e_time')) \
            .filter_by(event_type='ACCESS') \
            .group_by(Events.user_id) \
            .subquery()

        users_ = User.query.outerjoin(sub_query, sub_query.c.user_id == User.id) \
            .with_entities(User.id, User.first_name, User.last_name, User.email, User.is_admin,
                           sub_query.c.e_time.label('last_active')) \
            .all()

        if users_ is not None:
            return jsonify({'data': UsersSchema(many=True).dump(users_).data}), 200
        else:
            return jsonify({'data': []}), 200

    elif request.method == 'POST':
        action = request.form.get('action')

        if action != 'create' or action is None:
            abort(400)

        try:
            # TODO Not sure about change to dict (request.form.to_dict())
            action = _get_request_data(request.form)
        except ValueError:
            return jsonify({'error': 'ERROR_IN_REQUEST'})

        ret_data = list()

        for user in action.keys():
            name = action[user].get('first_name').title()
            lname = action[user].get('last_name').title()

            if action[user].get('is_admin', '0') == '1':
                if action[user].get('password', '') != '':
                    new_user = User(first_name=name,
                                    last_name=lname,
                                    email=action[user].get('email'),
                                    is_admin=1,
                                    password=hash_password(action[user].get('password')))
                else:
                    ret_data.append({'error': 'MISSING_PASSWORD'})
                    continue
            else:
                new_user = User(first_name=name,
                                last_name=lname,
                                email=action[user].get('email'))

            db.session.add(new_user)

            # Added users, try to commit
            try:
                db.session.commit()
            except (InternalError, IntegrityError) as e:
                db.session.rollback()
                current_app.logger.error('Could not add to database: {}'.format(e.args[0]))
                ret_data.append({'error': 'USER_ALREADY_EXISTS'})
                continue
            else:
                user_id = User.query.filter_by(email=action[user].get('email')).first()

                if user_id is not None:
                    new_user = UsersSchema().dump(user_id)
                    ret_data.append(new_user.data)

        return jsonify({'data': ret_data}), 201
    elif request.method == 'PUT':
        action = request.form.get('action')

        if action != 'edit' or action is None:
            abort(400)

        try:
            action = _get_request_data(request.form)
        except ValueError:
            return jsonify({'error': 'ERROR_IN_REQUEST'})

        ret_data = list()

        for user in action.keys():
            edit_user = User.query.filter_by(id=int(action[user].get('id'))).one_or_none()  # first none if not found

            if edit_user is not None:
                edit_user.first_name = action[user].get('first_name')
                edit_user.last_name = action[user].get('last_name')
                edit_user.email = action[user].get('email')

                if action[user].get('is_admin') == '1':
                    edit_user.is_admin = 1
                    edit_user.password = hash_password(action[user].get('password'))
                else:
                    edit_user.is_admin = 0
                    edit_user.password = ''

                try:
                    db.session.commit()
                except (InternalError, IntegrityError) as e:
                    db.session.rollback()
                    current_app.logger.error('Could not update database: {}'.format(e.args[0]))
                    ret_data.append({'error': 'COULD_NOT_UPDATE_RECORD',
                                     'id': action[user].get('id'),
                                     'first_name': action[user].get('first_name'),
                                     'last_name': action[user].get('last_name')})
                else:
                    edit_user = UsersSchema().dump(edit_user)
                    ret_data.append(edit_user.data)
            else:
                ret_data.append({'error': 'COULD_NOT_FIND_USER',
                                 'id': action[user].get('id'),
                                 'first_name': action[user].get('first_name'),
                                 'last_name': action[user].get('last_name')})

        return jsonify({'data': ret_data}), 200
    elif request.method == 'DELETE':
        action = request.args.get('action')

        if action != 'remove' or action is None:
            abort(400)

        try:
            action = _get_request_data(request.args)
        except ValueError:
            return jsonify({'error': 'ERROR_IN_REQUEST'})

        ret_data = list()

        for user in action.keys():
            if int(action[user].get('id')) != 1:  # Do not DELETE the admin account
                del_user = User.query.filter_by(id=int(action[user].get('id'))).one_or_none()

                if del_user is not None:
                    db.session.delete(del_user)

                    try:
                        db.session.commit()
                    except (InternalError, IntegrityError) as e:
                        current_app.logger.error('Count not delete record from database: {}'.format(e.args[0]))
                        ret_data.append({'error': 'COULD_NOT_DELETE_RECORD'})
                    else:
                        ret_data.append({})
                else:
                    abort(400)
            else:
                return jsonify({'error': 'CANNOT_DELETE_ADMIN_USER'})

        return jsonify({}), 204  # Return of empty JSON object is successful deletion.


@bp.route('/users/keycount/<int:user_id>', methods=['GET'])
@login_required
def key_count(user_id):
    """Gets the key count of each user

    +------+-----+
    | pin  |  1  |
    +------+-----+
    | rfid |  0  |
    +------+-----+
    | otp  |  0  |
    +------+-----+
    | totp |  1  |
    +------+-----+
    | u2f  |  0  |
    +------+-----+
    |rules |  0  |
    +------+-----+

    :param int user_id:

    :return: Key counts of user

    :rtype: {'data': ['pin': pin_count, 'rfid': rfid_count, 'otp': otp_count, 'totp': totp_count, 'u2f':u2f_count, 'rules':rules]}

    """
    pin_count = PinKey.query.with_entities(PinKey.user_id, count(PinKey.key).label('pin_count')) \
        .group_by(PinKey.user_id) \
        .subquery()
    rfid_count = RfidKey.query.with_entities(RfidKey.user_id, count(RfidKey.key).label('rfid_count')) \
        .group_by(RfidKey.user_id) \
        .subquery()
    otp_count = OtpKey.query.with_entities(OtpKey.user_id, count(OtpKey.key).label('otp_count')) \
        .group_by(OtpKey.user_id) \
        .subquery()
    totp_count = TotpKey.query.with_entities(TotpKey.user_id, count(TotpKey.key).label('totp_count')) \
        .group_by(TotpKey.user_id).subquery()
    u2f_count = U2fKey.query.with_entities(U2fKey.user_id, count(U2fKey.key).label('u2f_count')) \
        .group_by(U2fKey.user_id).subquery()
    rule_count = Rules.query.with_entities(Rules.user_id, count(Rules.days).label('rule_count')) \
        .group_by(Rules.user_id) \
        .subquery()

    keys_count = User.query \
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

    if keys_count is not None:
        return jsonify({'data': [{'pin': keys_count[0], 'rfid': keys_count[1], 'otp': keys_count[2], 'totp': keys_count[3],
                                  'u2f': keys_count[4], 'rules': keys_count[5]}]}), 200
    else:
        return jsonify({'data': [{'pin': 0, 'rfid': 0, 'otp': 0, 'totp': 0, 'u2f': 0, 'rules': 0}]}), 200


@bp.route('/users/keys/<int:user_id>/<string:protocol>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@login_required
def key_access(user_id, protocol):
    """Manages retrieval, addition, deletion and changing of keys

    :param int user_id:
    :param str protocol:

    :return: key data

    :rtype: GET returns key data {'data': ['key': (int), 'enabled': (bool), 'date_created': (datetime)]}
            POST returns single key {'data': ['key': (int), 'enabled': (bool), 'date_created': (datetime)]}
            PUT returns single key {'data': ['key': (int), 'enabled': (bool), 'date_created': (datetime)]}
            DELETE returns empty dict on success {}

    """
    if (protocol not in proto_dict) or (user_id is None):
        abort(400)

    if request.method == 'GET':
        user_keys = list()

        table = proto_dict[protocol][KEY_PROTOCOL]
        keys = table.query.filter_by(user_id=user_id).one_or_none()

        if keys is not None:
            dump = proto_dict[protocol][KEY_SCHEMA]().dump(keys).data
            dump['protocol'] = protocol
            user_keys.append(dump)

            return jsonify({'data': user_keys}), 200
        else:
            user_keys.append({'protocol': protocol})

            return jsonify({'data': user_keys})

    elif request.method == 'POST':
        key_class = proto_dict[protocol]
        key = request.form.get('key')
        key2 = request.form.get('key2')
        key3 = request.form.get('key3')
        cloud = None

        if (protocol == 'pin') or (protocol == 'totp') or (protocol == 'hotp'):
            key = int(key)

        if ((protocol == 'totp') or (protocol == 'hotp') or (protocol == 'u2f')) and (key2 is None):
            abort(400)

        if protocol == 'pin' or protocol == 'rfid':
            add_key = key_class[KEY_PROTOCOL](key=key, user_id=user_id)
        elif protocol == 'totp' or protocol == 'hotp':
            add_key = key_class[KEY_PROTOCOL](key=key, secret=key2, user_id=user_id)
        elif protocol == 'otp':
            """ Cloud service enrollment """
            if key3 != 'local':
                cloud = True
                add_key = key_class[KEY_PROTOCOL](key=key[:12],
                                                  private_identity=0,
                                                  aeskey=0,
                                                  counter=1,
                                                  time=1,
                                                  user_id=user_id,
                                                  remote_server=True)

            else:
                """ Local service enrollment """
                try:
                    public_id, otp_obj = decode_otp(bytes(key, encoding='utf-8'), bytes.fromhex(key2))
                except (CRCError, ValueError):
                    return jsonify({'error': 'AES Key Incorrect, validation failed'})

                add_key = key_class[KEY_PROTOCOL](key=public_id.decode('utf-8'),
                                                  private_identity=b2a_hex(otp_obj.uid).decode('utf-8'),
                                                  aeskey=key2,
                                                  counter=otp_obj.counter,
                                                  time=otp_obj.timestamp,
                                                  user_id=user_id)
        elif protocol == 'u2f':
            reg_data = RegistrationData(websafe_decode(key2))
            add_key = key_class[KEY_PROTOCOL](key=key,
                                              handle=reg_data.keyHandle,
                                              public_key=reg_data.publicKey,
                                              counter=1,
                                              transports='USB',
                                              user_id=user_id)
        db.session.add(add_key)

        try:
            db.session.commit()
        except (IntegrityError, InvalidRequestError) as e:
            db.session.rollback()
            current_app.logger.error('Unable to commit new key to database: {}'.format(e.orig.args[1]))
            return jsonify({'error': 'Unable to add key to database'})

        if cloud:
            cloud = OtpCloudService(yubico_user_name=key2, yubico_secret_key=key3, otp_key_key=add_key.key)
            db.session.add(cloud)

            try:
                db.session.commit()
            except (IntegrityError, InvalidRequestError, InternalError) as e:
                db.session.rollback()
                current_app.logger.error('Unable to commit new key to database: {}'.format(e.orig.args[1]))
                return jsonify({'error': 'Unable to add key to databae'})

        key = key_class[KEY_SCHEMA]().dump(add_key)

        return jsonify({'data': [key.data], 'success': 'Key Added Successfully'}), 201

    elif request.method == 'PUT':
        key_class = proto_dict[protocol]
        key_code = key_class[KEY_PROTOCOL].query.filter_by(user_id=user_id).first()

        if key_code is not None:
            key_code.enabled = True if key_code.enabled is False else False

            try:
                db.session.commit()
            except (IntegrityError, InvalidRequestError) as e:
                db.session.rollback()
                current_app.logger.error('Error committing to database: {}'.format(e.args[0]))
                abort(400)

            key_schema = key_class[KEY_SCHEMA]().dump(key_code)
            return jsonify({'data': key_schema.data}), 200
        else:
            return jsonify({'data': []})

    elif request.method == 'DELETE':
        key_class = proto_dict[protocol]
        del_key = key_class[KEY_PROTOCOL].query.filter_by(user_id=user_id).first()

        if del_key is not None:
            db.session.delete(del_key)
            try:
                db.session.commit()
            except (IntegrityError, InvalidRequestError) as e:
                db.session.rollback()
                current_app.logger.error('Could not delete from database: ' + e.args[0])
                abort(400)

        return jsonify({})


@bp.route('/users/keys/notify/<int:user_id>/<string:protocol>', methods=['GET'])
@login_required
def key_notify(user_id, protocol):
    """Notify user of key details

    This sends an email asynchronously to the user. In order for this to succeed, the email server settings
    need to be set in the database.

    :param int user_id:
    :param str protocol:
    :return: Result of notification
    :rtype: success {'success': 'message'} / error {'error': 'message'}
    """
    if protocol not in proto_dict:
        return jsonify({'error': 'INVALID_PROTOCOL'}), 400

    key_class = proto_dict[protocol][KEY_PROTOCOL]
    key = key_class.query.filter_by(user_id=user_id).one_or_none()
    user_name = None
    user_address = None
    key_code = None
    key_image = None

    if key is not None:
        user = User.query.filter_by(id=user_id).one_or_none()

        if user is None:
            return jsonify({'error': 'USER_NOT_FOUND'}), 400

        user_name = user.first_name + ' ' + user.last_name
        user_address = user.email
        key_code = key.key

        """ Generates the Image for TOTP """
        if protocol == 'totp':
            qrcode = pyqrcode.create(TOTP(key.secret).provisioning_uri(
                (user.first_name + ' ' + user.last_name), issuer_name='Modis Lock'))
            buffer = BytesIO()
            qrcode.png(buffer, scale=5)
            key_image = str(base64.b64encode(buffer.getvalue()))[2:-1]
            key_code = str(key_code) + ':' + key.secret
        elif protocol == 'otp':
            key_code = 'Not Used'

    send_email(user_address,
               subject='Key Access Enrollment',
               template='user_notification_email',
               user_name=user_name,
               key=protocol,
               key_code=str(key_code),
               key_image=key_image)

    return jsonify({'success': 'Sent Email'})


@bp.route('/users/key_gen', methods=['GET'])
@login_required
def get_code():
    """Gets unique PIN key

    PIN codes are what the system uses for protocol lookups, therefore it is important that the keys are unique.
    Length of the keys can be set from database settings.

    :return int: Unique key
    :rtype: {'code': pin_code}
    """
    pin_code = gen_unique_pin()

    return jsonify({'code': pin_code})


@bp.route('/users/<string:key_user>/<string:secret_code>.svg', methods=['GET'])
def qrcode_gen(key_user, secret_code):
    """QRCode Generator

    :param int key_user: User ID
    :param str secret_code: Random webcode generated from webpage
    :returns svg qrcode: SVG image of QRCode
    """
    """ Template for forming QR Code generation """
    qrcode = pyqrcode.create(TOTP(secret_code).provisioning_uri(key_user, issuer_name='Modis Lock'))
    buffer = io.BytesIO()
    qrcode.svg(buffer, scale=3)

    return str(buffer.getvalue(), 'utf-8'), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }


@bp.route('/users/gen_challenge', methods=['GET'])
@login_required
def gen_challenge():
    """Generates random web challenge for U2F registration

    :return: (challenge, appID)
    :rtype: {'challenge: challenge, 'appID': appID}
    """
    challenge = websafe_encode(os.urandom(43))
    appID = _get_app_id()

    return jsonify({'challenge': challenge, 'appID': appID}), 200


@cache.cached(timeout=60, key_prefix='get_ldap_add')
@bp.route('/users/ldap_add_users', methods=['GET', 'POST'])
@login_required
def ldap_add_users():
    """LDAP sync for differencing ldap users with local database users

    :return JSON: Result set
    """
    if request.method == 'GET':
        ldap_users = ldap_get_users()
        local_users = User.query.filter(User.uid.isnot(None)).all()
        mask = set((x.uid,) for x in local_users)
        difference = [x for x in ldap_users if (x.uid,) not in mask]
        marshed_data = LDAPUsersSchema(many=True).dump(difference)

        return jsonify({'data': marshed_data.data})

    elif request.method == 'POST':
        try:
            user_data = _get_request_data(request.form)
        except ValueError:
            return jsonify({'error': 'could not read request'}), 400

        user_count = 0

        for user in user_data.keys():
            new_user = User(uid=user_data[user].get('uid'),
                            first_name=user_data[user].get('first_name'),
                            last_name=user_data[user].get('last_name'),
                            email=user_data[user].get('email'))
            db.session.add(new_user)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                return jsonify({'error': 'unable to add to database'}), 400
            else:
                user_count += 1

        return jsonify({'success': str(user_count) + ' users added'})


@cache.cached(timeout=60, key_prefix='get_ldap_delete')
@bp.route('/users/ldap_delete_users', methods=['GET', 'POST'])
@login_required
def ldap_delete_users():
    """LDAP sync for differencing local database users with ldap users

    :return JSON: Result set
    """
    if request.method == 'GET':
        ldap_users = ldap_get_users()
        local_users = User.query.filter(User.uid.isnot(None)).all()
        mask = set((x.uid,) for x in ldap_users)
        difference = [x for x in local_users if (x.uid,) not in mask]
        marshed_data = LDAPUsersSchema(many=True).dump(difference)

        return jsonify({'data': marshed_data.data})

    elif request.method == 'POST':
        try:
            user_data = _get_request_data(request.form)
        except ValueError:
            return jsonify({'error': 'could not read request'}), 400

        user_count = 0

        for user in user_data.keys():
            user = User.query.filter(User.uid == user_data[user].get('uid')).first()

            if user is not None:
                db.session.delete(user)

                try:
                    db.session.commit()
                except:
                    db.session.rollback()
                    return jsonify({'error': 'unable to delete from database'}), 400
                else:
                    user_count += 1

        return jsonify({'success': str(user_count) + ' users deleted'})


@bp.route('/users', methods=['GET'])
@login_required
def users():
    """Main user management pages

    :returns html_template users.html:
    """
    ldap_enabled = Settings.query.filter(Settings.settings_name == 'OPTION_LDAP_ENABLE').first()

    ldap_enabled = False if (ldap_enabled is None or ldap_enabled.settings_value == 'False') else True

    return render_template('users/users.html', ldap_enabled=ldap_enabled)
