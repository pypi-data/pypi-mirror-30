
from flask import current_app
from ..extensions import db
from ..models import Settings, User
from sqlalchemy.exc import IntegrityError, InternalError, OperationalError
from ldap3 import Connection, Server, ALL, NTLM


def ldap_test(form):
    test_passed = True

    try:
        search_params = {
            'search_base': form['ldap_group_dn'] + ',' + form['ldap_base_dn'],
            'search_filter': form['ldap_search_filter'],
            'attributes': [form['ldap_mapping_field_username'],
                           form['ldap_mapping_field_f_name'],
                           form['ldap_mapping_field_email']]
        }
    except KeyError:
        return False

    try:
        server = Server(host=form['ldap_host'],
                        port=int(form['ldap_port']),
                        use_ssl=True if form['ldap_use_ssl'] == 'y' else False,
                        get_info=ALL)
        conn = Connection(server=server,
                          user=form['ldap_user_bind'],
                          password=form['ldap_password'],
                          authentication=NTLM if form['ldap_is_active_directory'] == 'y' else None)
    except KeyError:
        return False

    try:
        conn.bind()
    except:
        return False
    else:
        conn.search(**search_params)

        if conn.entries is None:
            test_passed = False
    finally:
        conn.unbind()

    return True if test_passed else False


def ldap_get_users():
    ldap_enabled = Settings.query.filter(Settings.settings_name == 'OPTION_LDAP_ENABLE').first()
    ldap_users = list()

    current_app.logger.debug('LDAP Enabled: {}'.format(ldap_enabled))
    if ldap_enabled is not None:
        ldap_enabled = True if ldap_enabled.settings_value == 'True' else False
        current_app.logger.debug('LDAP Enabled and starting to query remote')
        if ldap_enabled:
            ldap_params = Settings.query.filter(Settings.settings_name.like('LDAP%')).all()
            settings = dict()

            for params in ldap_params:
                if params.units == 'INT':
                    value = int(params.settings_value)
                elif params.units == 'BOOL':
                    value = True if params.settings_value == 'True' else False
                else:
                    value = params.settings_value
                settings[params.settings_name] = value

            search_params = {
                'search_base': settings['LDAP_GROUP_DN'] + ',' + settings['LDAP_BASE_DN'],
                'search_filter': settings['LDAP_USER_OBJECT_FILTER'],
                'attributes': [settings['LDAP_MAPPING_USERNAME'],
                               settings['LDAP_MAPPING_F_NAME'],
                               settings['LDAP_MAPPING_L_NAME'],
                               settings['LDAP_MAPPING_EMAIL']]
            }

            server = Server(host=settings['LDAP_HOST'],
                            port=settings['LDAP_PORT'],
                            use_ssl=settings['LDAP_USE_SSL'],
                            get_info=ALL)
            conn = Connection(server=server,
                              user=settings['LDAP_BIND_USER_DN'],
                              password=settings['LDAP_BIND_USER_PASSWORD'],
                              authentication=NTLM if settings['LDAP_USE_MS_AD'] else None)

            current_app.logger.debug('Server: {}\r\nPort: {}\r\nUser: {}\r\nPassword: {}'.format(settings['LDAP_HOST'],
                                                                                                 settings['LDAP_PORT'],
                                                                                                 settings['LDAP_BIND_USER_DN'],
                                                                                                 settings['LDAP_BIND_USER_PASSWORD']))

            try:
                conn.bind()
            except:
                current_app.logger.debug('Error in LDAP connection')
            else:
                conn.search(**search_params)

                for entry in conn.entries:
                    attrib = entry.entry_attributes_as_dict
                    uid = settings['LDAP_MAPPING_USERNAME']
                    first_name = settings['LDAP_MAPPING_F_NAME']
                    last_name = settings['LDAP_MAPPING_L_NAME']
                    email = settings['LDAP_MAPPING_EMAIL']
                    current_app.logger.debug('Found UID: {}'.format(attrib[uid][0]))

                    ldap_users.append(User(uid=attrib[uid][0],
                                           first_name=attrib[first_name][0],
                                           last_name=attrib[last_name][0],
                                           email=attrib[email][0]))
            finally:
                conn.unbind()
    return ldap_users


class LDAPSettings:
    """
    ldap_enable = BooleanField(label='LDAP Enabled',
                               description='Enable / Disable LDAP services')
    # URL to server ex. 192.168.0.81:389
    ldap_host = StringField(label='Host URL',
                            description='Host URL ex. 192.168.12.55',
                            placeholder='192.168.12.55')
    # Ldap port
    ldap_port = IntegerField(label='Port',
                             description='Port of LDAP server',
                             placeholder=389)
    # Base ex. DC=gas,DC=com,dc=vn
    ldap_base_dn = StringField(label='Base',
                               description='Base DN ex. dc=au,dc=modis,dc=io',
                               placeholder='dc=modis,dc=io')
    # Groups DN to be prepended to the Base DN
    ldap_group_dn = StringField(label='Base Search',
                                description='DN to be prepended to the base',
                                placeholder='ou=localusers')
    # Search filter LDAP_USER_OBJECT_FILTER
    ldap_search_filter = StringField(label='Search Filter',
                                     description='Specifies what object filter to apply when searching for users',
                                     placeholder='(objectclass=person)')
    # User
    ldap_user_bind = StringField(label='User DN',
                                 description='User with access to ldap server',
                                 placeholder='cn=admin,ou=admins,dc=modis,dc=io')
    # Password
    ldap_password = PasswordField(label='User password',
                                  description='Password for user with access to ldap server')
    # Mapping fields
    ldap_mapping_field_username = StringField(label='Username',
                                              description='Username mapped attribute',
                                              placeholder='cn')
    ldap_mapping_field_f_name = StringField(label='First Name',
                                            description='First name mapped attribute',
                                            placeholder='name')
    ldap_mapping_field_l_name = StringField(label='Last name',
                                            description='Last name mapped attribute')
    ldap_mapping_field_email = StringField(label='Email',
                                           description='Email mapped attribute')
    ldap_use_ssl = BooleanField(label='Use SSL connection',
                                description='Used with SSL connections')
    ldap_is_active_directory = BooleanField(label='Is Active Directory',
                                            description='Is this LDAP server a Microsoft Active directory server')

    """
    def __init__(self, form=None):
        if form is not None:
            for name in dir(form):
                if not name.startswith('_'):
                    unbound_field = getattr(form, name)
                    if hasattr(self, name):
                        setattr(self, name, unbound_field.data)

    def _get_value(self, value_name):
        value = Settings.query.filter(Settings.settings_name == value_name).first()

        return None if value is None else value.settings_value

    def _save_value(self, key, value):
        ldap = Settings.query.filter(Settings.settings_name == key).first()

        if ldap is not None:
            ldap.settings_value = value

            try:
                db.session.commit()
            except (IntegrityError, InternalError, OperationalError):
                db.session.rollback()

    @property
    def ldap_enable(self):
        ldap = self._get_value('OPTION_LDAP_ENABLE')
        return False if (ldap is None or ldap == 'False') else True

    @ldap_enable.setter
    def ldap_enable(self, enable):
        self._save_value('OPTION_LDAP_ENABLE', 'True' if (enable == 'y' or enable is True) else 'False')

    @property
    def ldap_host(self):
        host = self._get_value('LDAP_HOST')
        return '' if host is None else host

    @ldap_host.setter
    def ldap_host(self, hname):
        self._save_value('LDAP_HOST', hname)

    @property
    def ldap_port(self):
        port = self._get_value('LDAP_PORT')
        return 0 if port is None else port

    @ldap_port.setter
    def ldap_port(self, port):
        if isinstance(port, int):
            self._save_value('LDAP_PORT', str(port))

    @property
    def ldap_base_dn(self):
        base = self._get_value('LDAP_BASE_DN')
        return '' if base is None else base

    @ldap_base_dn.setter
    def ldap_base_dn(self, base_value):
        if isinstance(base_value, str):
            self._save_value('LDAP_BASE_DN', base_value)

    @property
    def ldap_group_dn(self):
        group = self._get_value('LDAP_GROUP_DN')
        return '' if group is None else group

    @ldap_group_dn.setter
    def ldap_group_dn(self, base_value):
        if isinstance(base_value, str):
            self._save_value('LDAP_GROUP_DN', base_value)

    @property
    def ldap_search_filter(self):
        search = self._get_value('LDAP_USER_OBJECT_FILTER')
        return '' if search is None else search

    @ldap_search_filter.setter
    def ldap_search_filter(self, filter):
        if isinstance(filter, str):
            self._save_value('LDAP_USER_OBJECT_FILTER', filter)

    @property
    def ldap_user_bind(self):
        user = self._get_value('LDAP_BIND_USER_DN')
        return '' if user is None else user

    @ldap_user_bind.setter
    def ldap_user_bind(self, user):
        if isinstance(user, str):
            self._save_value('LDAP_BIND_USER_DN', user)

    @property
    def ldap_password(self):
        password = self._get_value('LDAP_BIND_USER_PASSWORD')
        return '' if password is None else password

    @ldap_password.setter
    def ldap_password(self, password):
        if isinstance(password, str):
            self._save_value('LDAP_BIND_USER_PASSWORD', password)

    @property
    def ldap_mapping_field_username(self):
        username = self._get_value('LDAP_MAPPING_USERNAME')
        return '' if username is None else username

    @ldap_mapping_field_username.setter
    def ldap_mapping_field_username(self, username):
        if isinstance(username, str):
            self._save_value('LDAP_MAPPING_USERNAME', username)

    @property
    def ldap_mapping_field_f_name(self):
        f_name = self._get_value('LDAP_MAPPING_F_NAME')
        return '' if f_name is None else f_name

    @ldap_mapping_field_f_name.setter
    def ldap_mapping_field_f_name(self, f_name):
        if isinstance(f_name, str):
            self._save_value('LDAP_MAPPING_F_NAME', f_name)

    @property
    def ldap_mapping_field_l_name(self):
        l_name = self._get_value('LDAP_MAPPING_L_NAME')
        return '' if l_name is None else l_name

    @ldap_mapping_field_l_name.setter
    def ldap_mapping_field_l_name(self, l_name):
        if isinstance(l_name, str):
            self._save_value('LDAP_MAPPING_L_NAME', l_name)

    @property
    def ldap_mapping_field_email(self):
        email = self._get_value('LDAP_MAPPING_EMAIL')
        return '' if email is None else email

    @ldap_mapping_field_email.setter
    def ldap_mapping_field_email(self, email):
        if isinstance(email, str):
            self._save_value('LDAP_MAPPING_EMAIL', email)

    @property
    def ldap_use_ssl(self):
        ssl = self._get_value('LDAP_USE_SSL')
        return False if (ssl is None or ssl == 'False') else True

    @ldap_use_ssl.setter
    def ldap_use_ssl(self, use_ssl):
        if isinstance(use_ssl, bool):
            self._save_value('LDAP_USE_SSL', 'True' if (use_ssl == 'y') else 'False')

    @property
    def ldap_is_active_directory(self):
        ms_ad = self._get_value('LDAP_USE_MS_AD')
        return False if (ms_ad is None or ms_ad == 'False') else True

    @ldap_is_active_directory.setter
    def ldap_is_active_directory(self, is_ms_ad):
        if isinstance(is_ms_ad, bool):
            self._save_value('LDAP_USE_MS_AD', 'True' if (is_ms_ad == 'y') else 'False')
