import logging

from chapman2 import task


log = logging.getLogger(__name__)

@task
def log_message(message, *args):
    log.info(message, *args)

