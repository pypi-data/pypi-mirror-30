"""Shell command."""
import logging

from cliff.command import Command
from IPython import embed

from chapman2 import model as M

log = logging.getLogger(__name__)


class Shell(Command):
    """Run an interactive shell."""

    def take_action(self, parsed_args):
        log.info('Run Chapman2 Shell')
        embed()
