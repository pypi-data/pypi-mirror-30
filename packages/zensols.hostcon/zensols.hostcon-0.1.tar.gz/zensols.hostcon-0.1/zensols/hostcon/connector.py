import logging, socket, re, os, getpass

from subprocess import call

from zensols.actioncli import SimpleActionCli
from zensols.actioncli import Config

logger = logging.getLogger('zensols.env.conn')

class Connector(object):
    """Connect to a host via xterm, ssh login, etc.

    """
    def __init__(self, config, host_name, user_name=None, dry_run=False, domain=None):
        self.config = config
        self.host_name = host_name
        self._user_name = user_name
        self.dry_run = dry_run
        self._domain = domain

    @property
    def domain(self):
        if self._domain != None:
            return self._domain
        else:
            hname = socket.getfqdn()
            logger.debug('fqdn: %s' % hname)
            if hname == '1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.ip6.arpa':
                return None
            elif hname == '1.0.0.127.in-addr.arpa':
                return None
            else:
                match = re.match(r'^[^.]+\.(.+)$', hname)
                return match.group(1) if match else hname

    @property
    def user_name(self):
        if self._user_name != None:
            return self._user_name
        else:
            return getpass.getuser()

    def _get_params_section(self, section):
        sections = self.config.sections
        logger.debug('param search in %s for sections: %s' % (section, sections))
        if sections and section in sections:
            host_params = self.config.get_options(section, vars=os.environ)
            return host_params

    def _get_params_from_config(self, section_prefix=None):
        domain = self.domain
        logger.debug('domain: %s' % domain)
        if section_prefix: section_prefix = section_prefix + ' '
        else: section_prefix = ''
        domain = '.' + domain if domain else ''
        init_section = '%s%s%s' % (section_prefix, self.host_name, domain)
        section = init_section
        logger.debug('section: %s' % section)
        host_params = self._get_params_section(section)
        if not host_params:
            section = '%s %s' % (self.host_name, self.config.default_section)
            host_params = self._get_params_section(section)
        if not host_params:
            # for error message
            section = '<%s>, <%s %s> or <%s>' % (init_section, self.host_name, self.config.default_section, self.config.default_section)
            host_params = self.config.get_options(vars=os.environ)
        if not 'user_name' in host_params:
            host_params['user_name'] = self.user_name
        if not 'host_name' in host_params:
            host_params['host_name'] = self.host_name
        host_params['section'] = section
        logger.debug('params: %s' % host_params)
        return host_params

    @property
    def command_keys(self):
        return 'host_name domain user_name ssh_port ssh_switches type'.split(' ')

    @property
    def mount_keys(self):
        return 'remote_mount_point local_mount_point'.split(' ')

    @property
    def context_keys(self):
        return 'ssh_switches'.split(' ')

    def get_params(self, section_prefix=None, command_keys=None, optional_keys=[]):
        params = self._get_params_from_config(section_prefix)
        logger.debug('params: <%s>, domain: %s' % (params, self.domain))
        params['domain'] = self.domain
        context_keys = self.context_keys
        for k in context_keys:
            params[k] = None
        params.update(self.config.get_options(opt_keys=context_keys, vars=os.environ))
        command_keys = command_keys if command_keys else self.command_keys
        logger.debug('command keys: %s' % command_keys)
        cmd_keys = set(command_keys) - {'type'}
        opt_keys = params.keys() & set(optional_keys)
        logger.debug('params: <%s>, command keys: <%s>' % (params, cmd_keys))
        params_sub = {k: params[k] for k in (params.keys() & cmd_keys) | opt_keys}
        logger.debug('params_sub: %s' % params_sub)
        for p in cmd_keys:
            logger.debug('cmd key set: %s' % p)
            if not p in params_sub:
                raise ValueError('missing configuration key \'%s\' for section: %s' % (p, params['section']))
        return params_sub

    def print_info(self):
        params = self.get_params()
        ctx_keys = set(self.context_keys)
        for k in sorted(self.command_keys):
            if k in params and not k in ctx_keys:
                kname = k.replace('_', '-')
                print('%s: %s' % (kname, params[k]))

    def print_environment(self):
        params = self.get_params()
        ctx_keys = set(self.context_keys)
        for k in sorted(self.command_keys):
            if k in params and not k in ctx_keys:
                kname = k.upper()
                print('export %s=%s' % (kname, params[k]))

    def get_command_args_lists(self, conn_type):
        if conn_type == 'mount': return self._get_command_mount_args()
        elif conn_type == 'umount': return self._get_command_umount_args()
        else: return self._get_command_default_args(conn_type)

    def _get_command_mount_args(self):
        params = self.get_params(optional_keys=['mounts'])
        mounts = params['mounts'] if 'mounts' in params else ''
        mounts = re.split('[ ,]', mounts)
        cmds = []
        for mname in mounts:
            logger.debug('mount found: %s' % mname)
            params.update(self.get_params(section_prefix=mname, command_keys=self.mount_keys))
            addr = '%(user_name)s@%(host_name)s:%(remote_mount_point)s' % params
            args = ['sshfs', addr]
            args.append(params['local_mount_point'])
            mount_opts = self.config.get_option('mount_options')
            ssh_opts = '-oport=' + params['ssh_port']
            if mount_opts: ssh_opts = ssh_opts + ',' + mount_opts
            ssh_opts = ssh_opts + ',volname=' + mname
            args.append(ssh_opts)
            cmds.append(args)
        return cmds

    def _get_command_umount_args(self):
        params = self.get_params(optional_keys=['mounts'])
        mounts = params['mounts'] if 'mounts' in params else ''
        mounts = re.split('[ ,]', mounts)
        cmds = []
        for mname in mounts:
            logger.debug('mount found: %s' % mname)
            params.update(self.get_params(section_prefix=mname, command_keys=self.mount_keys))
            args = ['umount', params['local_mount_point']]
            cmds.append(args)
        return cmds

    def _get_command_default_args(self, conn_type):
        params = self.get_params()
        conn_cfg = {'xterm': ['/usr/bin/xterm', 'ssh', ['-f']],
                    'login': [None, 'ssh', []],
                    'emacs': ['/usr/local/emacs/bin/emacs', 'ssh', ['-f']],
                    }[conn_type]
        conn_type, bin_name, extra_args = conn_cfg
        args = [bin_name]
        params['type'] = conn_type
        if params['ssh_switches']:
            args.extend(params['ssh_switches'].split(' '))
        args.extend(extra_args)
        addr = '%(user_name)s@%(host_name)s' % params
        args.extend(['-p', params['ssh_port'], addr, conn_type])
        args = list(filter(lambda x: x != None, args))
        return [args]

    def _args_to_command(self, args):
        return ' '.join(args)

    def get_commands(self, conn_type, single_command=False):
        args_list = self.get_command_args_lists(conn_type)
        if single_command: return args_list
        else: return list(map(lambda x: self._args_to_command(x), args_list))

    def exec_commands(self, conn_type):
        args_list = self.get_commands(conn_type, single_command=True)
        for args in args_list:
            cmd = self._args_to_command(args)
            logger.info('invoking %s' % cmd)
            if not self.dry_run:
                logger.debug('args: %s' % args)
                call(args)

    def exec_mount(self):
        self.exec_commands('mount')

    def exec_umount(self):
        self.exec_commands('umount')

    def exec_login(self):
        self.exec_commands('login')

    def exec_xterm(self):
        self.exec_commands('xterm')

    def exec_emacs(self):
        self.exec_commands('emacs')
