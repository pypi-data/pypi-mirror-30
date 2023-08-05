import os

from jutil.configuration import config_singleton

from ScopusWp.config import PROJECT_PATH

NAME = 'scopus'
DB_NAME = '__scopus'
PATH = os.path.dirname(os.path.realpath(__file__))


class ScopusConfig(config_singleton(
    os.path.join(PROJECT_PATH, 'scopus'),
    'config.ini'
)):
    pass
