import os


class Config(object):
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
