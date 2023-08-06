import os
from configparser import ConfigParser
from zensols.actioncli import SimpleActionCli, Config
from zensols.hostcon import Connector

class AppConfig(Config):
    def __init__(self, config_file=None, default_section='default'):
        Config.__init__(self, config_file, default_section)

    def _create_config_parser(self):
        inter = configparser.ExtendedInterpolation()
        #return configparser.ConfigParser(defaults=self.defaults, interpolation=inter)
        return configparser.ConfigParser(interpolation=inter)

class AppCommandLine(SimpleActionCli):
    def __init__(self, conf_file=None):
        opts = {'host_name', 'dry_run'}
        exec_name = 'connector'
        executors = {exec_name: lambda params: Connector(**params)}
        invokes = {'info': [exec_name, 'print_info', 'print configuration info'],
                   'env': [exec_name, 'print_environment', 'print info as environment variables'],
                   'xterm': [exec_name, 'exec_xterm', 'start an xterm on host'],
                   'emacs': [exec_name, 'exec_emacs', 'start emacs on the host'],
                   'mount': [exec_name, 'exec_mount', 'mount directories from host locally'],
                   'umount': [exec_name, 'exec_umount', 'un-mount directories'],
                   'login': [exec_name, 'exec_login', 'slogin to host']}
        conf = Config(conf_file)
        default_action = conf.get_option('action')
        SimpleActionCli.__init__(self, executors, invokes, config=conf,
                                 manditory_opts=opts, opts=opts,
                                 default_action=default_action)

    def config_parser(self):
        parser = self.parser
        self._add_whine_option(parser, 1)
        parser.add_option('-n', '--hostname', dest='host_name',
                          help='the host to connect to')
        parser.add_option('-d', '--dryrun', dest='dry_run',
                          action="store_true", default=False,
                          help='dry run to not actually connect, but act like it')

def main():
    conf_env_var='HOSTCONRC'
    if conf_env_var in os.environ:
        default_config_file = os.environ[conf_env_var]
    else:
        default_config_file = '%s/.hostconrc' % os.environ['HOME']
    cl = AppCommandLine(default_config_file)
    cl.invoke()
