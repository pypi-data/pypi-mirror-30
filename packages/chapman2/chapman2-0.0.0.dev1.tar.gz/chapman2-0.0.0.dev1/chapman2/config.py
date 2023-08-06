import os
from . import errors


def config_from_env(prefix='CHAPMAN_'):
    try:
        return dict(
            MONGODB_URI=os.environ[prefix + 'MONGODB_URI'],
            LOGCONFIG=os.environ[prefix + 'LOGCONFIG'])
    except KeyError as ke:
        raise errors.ConfigError('missing env var: {}'.format(ke))
