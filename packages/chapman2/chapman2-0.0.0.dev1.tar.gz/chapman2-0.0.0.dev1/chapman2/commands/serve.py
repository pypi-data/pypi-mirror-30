import time
import uuid
import logging
import importlib

from cliff.command import Command

from chapman2 import model, Task

log = logging.getLogger(__name__)


class Serve(Command):
    """Run locally."""

    def get_parser(self, prog_name):
        parser = super(Serve, self).get_parser(prog_name)
        parser.add_argument(
            '--debug-server', action='store_true',
            help='Use debug mode')
        parser.add_argument(
            '--worker-name', default=None,
            help='Unique name for worker')
        parser.add_argument(
            'modules', nargs='+', help='Task modules to import')
        return parser

    def take_action(self, parsed_args):
        worker = parsed_args.worker_name
        if worker is None:
            worker = str(uuid.uuid4())
        for mod in parsed_args.modules:
            log.info('Importing task module %s', mod)
            importlib.import_module(mod)
        log.info('Worker %s ready...', worker)
        while True:
            msg = model.Message.reserve(worker)
            if msg is None:
                time.sleep(1)
                continue
            try:
                t = Task.lookup(msg.task)
                log.info('Handle %s', t)
                result = t.run(msg.payload)
                log.info('...result %s', result)
                msg.m.delete()
            except Exception as err:
                log.exception('Task error')
                msg.error(repr(err))
