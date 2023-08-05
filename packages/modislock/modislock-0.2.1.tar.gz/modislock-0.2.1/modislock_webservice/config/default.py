# coding: utf-8
import os


class Config(object):
    """Base config class."""
    VERSION = 0.1

    # Flask app config
    DEBUG = False
    TESTING = False
    SECRET_KEY = "\xb5\xb3}#\xb7A\xcac\x9d0\xb6\x0f\x80z\x97\x00\x1e\xc0\xb8+\xe9)\xf0}"
    PERMANENT_SESSION_LIFETIME = 60 * 20  # 20 Minutes
    SESSION_COOKIE_NAME = 'modislock_session'
    WTF_CSRF_TIME_LIMIT = PERMANENT_SESSION_LIFETIME

    # Root path of project
    PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))

    # Site domain
    SITE_TITLE = "Modis Lock"
    SITE_DOMAIN = "https://modislock.local"

    # SQLAlchemy config
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://modisweb:l3j4lkjlskjd@localhost/modislock"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_POOL_RECYCLE = 500

    # Security
    # We're using PBKDF2 with salt.
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_PASSWORD_SALT = SECRET_KEY
    SECURITY_RECOVERABLE = True

    LOGIN_DISABLED = False
    WTF_CSRF_ENABLED = True

    # Flask-DebugToolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # Host string, used by fabric
    HOST_STRING = "root@localhost"

    # Upload folder for database restore
    UPLOAD_FOLDER = '/tmp/'

    # Caching
    CACHE_TYPE = 'simple'

    # Assets
    ASSETS_DEBUG = False
    ASSETS_AUTO_BUILD = False
    MINIFY_PAGE = True

    # ADMIN
    ADMIN_USER = 'modis'
    ADMIN_PASSWORD = 'modis'

    # Python version check
    REQUIRED_PYTHON_VER = (3, 5, 0)

    # Celery
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

    # Mail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'modislock@gmail.com'
    MAIL_PASSWORD = 'mypassword'
    MAIL_DEFAULT_SENDER = 'modislock@gmail.com'
    MAIL_SUBJECT_PREFIX = 'Modis Lock:'

