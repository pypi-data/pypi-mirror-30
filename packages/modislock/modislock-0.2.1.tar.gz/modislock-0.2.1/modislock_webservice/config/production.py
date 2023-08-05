# coding: utf-8
from .default import Config


class ProductionConfig(Config):
    # Session config
    SESSION_COOKIE_NAME = 'modislock_session'

    # Site domain
    SITE_DOMAIN = "https://modislock.local"
