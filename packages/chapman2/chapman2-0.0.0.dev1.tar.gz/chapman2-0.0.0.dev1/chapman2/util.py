import os
import logging
import traceback

import ipdb

log = logging.getLogger(__name__)


def debug_hook(type, value, tb):
    """Launch the ipdb debugger on errors."""
    traceback.print_exception(type, value, tb)
    print
    ipdb.pm()


def load_envfile(filename):
    with open(filename) as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            if line.startswith('#'):
                continue
            kvdata = line.strip().split('=', 1)
            if len(kvdata) != 2:
                log.warning('bad .env line %r', line)
                continue
            key, val = kvdata
            os.environ[key] = val
