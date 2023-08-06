import os
import sys
import logging.config
from urllib.parse import urlparse

import yaml
import pymongo
from cliff.app import App
from cliff.commandmanager import CommandManager

from chapman2 import util, config, model


log = logging.getLogger(__name__)


def main(argv=sys.argv[1:]):
    myapp = ChapmanApp()
    return myapp.run(argv)


class ChapmanApp(App):

    def __init__(self):
        super(ChapmanApp, self).__init__(
            description='Chapman App',
            version='0.1',
            command_manager=CommandManager('chapman2.commands'),
            deferred_help=True)

    def initialize_app(self, argv):
        super(ChapmanApp, self).initialize_app(argv)
        if self.options.pdb:
            sys.excepthook = util.debug_hook

    def prepare_to_run_command(self, cmd):
        if os.path.exists('.env'):
            util.load_envfile('.env')
        self.config = config.config_from_env(self.options.config_prefix)
        with open(self.config['LOGCONFIG']) as fp:
            logging.config.dictConfig(yaml.load(fp))
        self.c2_initialize_model()

    def c2_initialize_model(self):
        cli = pymongo.MongoClient(self.config['MONGODB_URI'])
        pr = urlparse(self.config['MONGODB_URI'])
        dbname = pr.path[1:]
        model.metadata.bind(cli[dbname])

    def configure_logging(self):
        '''Turn OFF cliff's default logging'''
        pass

    def build_option_parser(self, description, version, argparse_kwargs=None):
        parser = super(ChapmanApp, self).build_option_parser(
            description, version, argparse_kwargs)
        parser.add_argument('--pdb', action='store_true')
        parser.add_argument('--config-prefix', default='CHAPMAN_')
        return parser


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
