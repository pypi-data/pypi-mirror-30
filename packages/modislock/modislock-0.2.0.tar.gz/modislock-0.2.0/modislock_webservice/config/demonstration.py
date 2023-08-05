# coding: utf-8
from .default import Config


class DemoConfig(Config):
    # Host string, used by fabric
    HOST_STRING = "root@172.104.135.149"
    SITE_DOMAIN = "http://demo.modis.io"

