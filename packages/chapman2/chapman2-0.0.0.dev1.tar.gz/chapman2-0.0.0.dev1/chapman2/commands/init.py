"""Shell command."""
import logging

from cliff.command import Command

from chapman2 import model as M

log = logging.getLogger(__name__)


class Initialize(Command):
    """Create an initial environment."""

    def get_parser(self, prog_name):
        parser = super(Initialize, self).get_parser(prog_name)
        parser.add_argument(
            '--drop', action='store_true', help='Drop collections?')
        return parser

    def take_action(self, parsed_args):
        log.info('Initialize Chapman2 Database')
        if parsed_args.drop:
            for coll in M.metadata.collections:
                log.info('... drop %s', coll)
                coll.m.drop()
        for coll in M.metadata.collections:
            log.info('... create %s', coll)
            coll.m.drop_indexes()
            for idx in coll.m.indexes:
                idx.create(coll.m.collection)
        log.info('Done')