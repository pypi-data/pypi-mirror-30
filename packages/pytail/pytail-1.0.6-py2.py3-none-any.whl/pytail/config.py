"""pyTail configuration"""
import os
import json
import argparse
import logging


class ConfigParamsGroup(object):
    """Used to map groups"""

    #  pylint: disable=too-few-public-methods

    def __init__(self, name, description=None):
        self.name = name
        self.description = description if description else None


class ConfigParams(object):
    """Used to configure the params"""

    #  pylint: disable=too-few-public-methods

    def __init__(self, **kwargs):
        self.default = kwargs.get('default', '')
        self.description = kwargs.get('description', '')
        self.islist = kwargs.get('islist', False)
        self.action = kwargs.get('action', 'store')
        self.cmdonly = kwargs.get('cmdonly', False)

        if isinstance(kwargs.get('group', False), ConfigParamsGroup):
            self.group = kwargs.get('group')
        else:
            self.group = False

        if not isinstance(kwargs.get('type', False), type):
            self.type = type(self.default)
        else:
            self.type = kwargs.get('type')

        if self.islist and not isinstance(self.default, list):
            self.default = [self.type(self.default)]


class Config(object):
    """Object that holds configuration"""

    def __config_file(self):
        return os.path.join(self.__cmdargs.config, 'pytail.json')

    def __prepare_cmd_parser(self):
        parser = argparse.ArgumentParser(description='pyTail')
        existing_groups = {}
        for key, value in self.default_config.items():
            argloc = parser
            if value.group:
                if value.group.__hash__() not in existing_groups.keys():
                    group = parser.add_argument_group(value.group.name,
                                                      value.group.description)
                    existing_groups[value.group.__hash__()] = group
                else:
                    group = existing_groups[value.group.__hash__()]
                argloc = group
            pkwargs = {
                'help': value.description,
                'default': value.default,
                'action': value.action
                }
            if value.action != 'store_true' and not value.islist:
                pkwargs['type'] = value.type
            argloc.add_argument('--%s' % key.replace('_', '-'), **pkwargs)
        return parser

    def __parse_cmd(self):
        return self.__prepare_cmd_parser().parse_args()

    def __parse_config_file(self):
        cfile = self.__config_file()
        if os.path.exists(cfile) and os.path.isfile(cfile):
            with open(cfile, 'r') as jfile:
                jconfig = json.load(jfile)
                for key, value in jconfig.items():
                    if key in self.default_config.keys() and \
                            not self.default_config[key].cmdonly and \
                            value != self.default_config[key].default:
                        self.configs[key] = value

    def __parse_cmd_configs(self):
        for key, value in vars(self.__cmdargs).items():
            if key in self.magic().keys():
                continue
            dconfig = self.default_config[key]
            if dconfig.cmdonly:
                continue
            if dconfig.islist:
                if ',' in value:
                    value = value.split(',')
                else:
                    value = [value]
                value = [dconfig.type(x) for x in value]
            load_config = True
            if key in self.configs.keys():
                load_config = value != self.default_config[key].default
            if load_config:
                self.configs[key] = value

    def __init__(self):
        group_common = ConfigParamsGroup('Common', 'Common options')
        group_tcp = ConfigParamsGroup('TCP', 'TCP Server Configuration')
        group_log = ConfigParamsGroup('Logging', 'Logging configuration')
        self.default_config = {
            'paths': ConfigParams(default='/var/log/$file.log', islist=True,
                                  description='List of paths where '
                                  'possible tailed files may live. Use $file '
                                  'to place the filename provived by the user.'
                                  'It\'s ignored when file arg is set',
                                  group=group_common),
            'file': ConfigParams(default=None, type=str, group=group_common,
                                 description='Single file to tail'),
            'tcp_port': ConfigParams(default=8081,
                                     description='TCP Port where the socket '
                                     'will listen', group=group_tcp),
            'tcp_host': ConfigParams(default='127.0.0.1',
                                     description='TCP Address where the '
                                     'socket will listen', group=group_tcp),
            'tcp_timeout': ConfigParams(default=5, group=group_tcp,
                                        description='TCP Timeout in seconds'),
            'logfile': ConfigParams(default=None, description='pyTail log',
                                    type=str, group=group_log),
            'loglevel': ConfigParams(default=logging.INFO, group=group_log,
                                     description='pyTail log level'),
            'logformat': ConfigParams(default='%(asctime)s %(levelname)s '
                                      '%(message)s',
                                      description='pyTail log format',
                                      group=group_log),
            'config': ConfigParams(default='/etc/pytail', cmdonly=True,
                                   description='Configuration directory',
                                   group=group_common),
            'save': ConfigParams(default=False, cmdonly=True,
                                 description='Save current configuration',
                                 action='store_true', group=group_common),
            }
        self.configs = {}
        self.__cmdargs = self.__parse_cmd()
        self.__parse_config_file()
        self.__parse_cmd_configs()

        if self.__cmdargs.save:
            with open(self.__config_file(), 'w') as jfile:
                json.dump(self.configs, jfile, indent=4)

        # Magic values
        for key, value in self.magic().items():
            self.configs[key] = value

    @staticmethod
    def magic():
        """Get magic, constant configurations"""
        return {}

    def get(self, *args, **kwargs):
        """Get configuration"""
        return self.configs.get(*args, **kwargs)
