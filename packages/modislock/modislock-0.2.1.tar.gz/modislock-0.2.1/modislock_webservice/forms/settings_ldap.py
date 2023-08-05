# coding: utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, PasswordField, IntegerField
from wtforms.validators import DataRequired, IPAddress, NumberRange
from wtforms.widgets import PasswordInput


class SettingsLDAPForm(FlaskForm):
    """
    self.config.setdefault('LDAP_PORT', 389)
    self.config.setdefault('LDAP_HOST', None)
    self.config.setdefault('LDAP_USE_SSL', False)
    self.config.setdefault('LDAP_READONLY', True)
    self.config.setdefault('LDAP_BIND_DIRECT_CREDENTIALS', False)
    self.config.setdefault('LDAP_BIND_DIRECT_SUFFIX', '')
    self.config.setdefault('LDAP_BIND_DIRECT_GET_USER_INFO', True)
    self.config.setdefault('LDAP_ALWAYS_SEARCH_BIND', False)
    self.config.setdefault('LDAP_BASE_DN', '')
    self.config.setdefault('LDAP_BIND_USER_DN', None)
    self.config.setdefault('LDAP_BIND_USER_PASSWORD', None)
    self.config.setdefault('LDAP_SEARCH_FOR_GROUPS', True)
    self.config.setdefault('LDAP_FAIL_AUTH_ON_MULTIPLE_FOUND', False)

    # Prepended to the Base DN to limit scope when searching for
    # Users/Groups.
    self.config.setdefault('LDAP_USER_DN', '')
    self.config.setdefault('LDAP_GROUP_DN', '')

    self.config.setdefault('LDAP_BIND_AUTHENTICATION_TYPE', 'SIMPLE')

    # Ldap Filters
    self.config.setdefault('LDAP_USER_SEARCH_SCOPE', 'LEVEL')
    self.config.setdefault('LDAP_USER_OBJECT_FILTER', '(objectclass=person)')
    self.config.setdefault('LDAP_USER_LOGIN_ATTR', 'uid')
    self.config.setdefault('LDAP_USER_RDN_ATTR', 'uid')
    self.config.setdefault('LDAP_GET_USER_ATTRIBUTES', ldap3.ALL_ATTRIBUTES)

    self.config.setdefault('LDAP_GROUP_SEARCH_SCOPE', 'LEVEL')
    self.config.setdefault('LDAP_GROUP_OBJECT_FILTER', '(objectclass=group)')
    self.config.setdefault('LDAP_GROUP_MEMBERS_ATTR', 'uniqueMember')
    self.config.setdefault('LDAP_GET_GROUP_ATTRIBUTES', ldap3.ALL_ATTRIBUTES)
    self.config.setdefault('LDAP_ADD_SERVER', True)

    if self.config['LDAP_ADD_SERVER']:
        self.add_server(
            hostname=self.config['LDAP_HOST'],
            port=self.config['LDAP_PORT'],
            use_ssl=self.config['LDAP_USE_SSL']
        )
    """

    ldap_enable = BooleanField(label='LDAP Enabled',
                               description='Enable / Disable LDAP services')
    # URL to server ex. 192.168.0.81:389
    ldap_host = StringField(label='Host URL',
                            description='Host URL ex. 192.168.12.55',
                            validators=[DataRequired('Host required')])
    # Ldap port
    ldap_port = IntegerField(label='Port',
                             description='Port of LDAP server',
                             validators=[DataRequired('A valid port number is required')])
    # Base ex. DC=gas,DC=com,dc=vn
    ldap_base_dn = StringField(label='Base',
                               description='Base DN ex. dc=au,dc=modis,dc=io',
                               validators=[DataRequired('Base to search from is required')])
    # Groups DN to be prepended to the Base DN
    ldap_group_dn = StringField(label='Base Search',
                                description='DN to be prepended to the base')
    # Search filter LDAP_USER_OBJECT_FILTER
    ldap_search_filter = StringField(label='Search Filter',
                                     description='Specifies what object filter to apply when searching for users',
                                     validators=[DataRequired('Search filter required')])
    # User
    ldap_user_bind = StringField(label='User DN',
                                 description='User with access to ldap server',
                                 validators=[DataRequired('User with access to LDAP required')])
    # Password
    ldap_password = PasswordField(label='User password',
                                  description='Password for user with access to ldap server',
                                  widget=PasswordInput(hide_value=False),
                                  validators=[DataRequired('Password for LDAP user required')])
    # Mapping fields
    ldap_mapping_field_username = StringField(label='Username',
                                              description='Username mapped attribute',
                                              validators=[DataRequired('Attribute for username required')])
    ldap_mapping_field_f_name = StringField(label='First Name',
                                            description='First name mapped attribute',
                                            validators=[DataRequired('First name attribute required')])
    ldap_mapping_field_l_name = StringField(label='Last name',
                                            description='Last name mapped attribute',
                                            validators=[DataRequired('Last name attribute required')])
    ldap_mapping_field_email = StringField(label='Email',
                                           description='Email mapped attribute',
                                           validators=[DataRequired('Email attribute required')])
    ldap_use_ssl = BooleanField(label='Use SSL connection',
                                description='Used with SSL connections')
    ldap_is_active_directory = BooleanField(label='Is Active Directory',
                                            description='Is this LDAP server a Microsoft Active directory server')

    submit_ldap_btn = SubmitField(label='Save LDAP Settings', description='Save LDAP')
