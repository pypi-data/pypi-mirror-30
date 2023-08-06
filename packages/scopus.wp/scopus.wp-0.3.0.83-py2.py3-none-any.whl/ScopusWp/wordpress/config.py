from ScopusWp.config import PROJECT_PATH

from jutil.configuration import config_singleton

import os


NAME = 'wordpress'
PATH = os.path.dirname(os.path.realpath(__file__))


class WordpressConfig(config_singleton(
    os.path.join(PROJECT_PATH, 'wordpress'),
)):
    pass