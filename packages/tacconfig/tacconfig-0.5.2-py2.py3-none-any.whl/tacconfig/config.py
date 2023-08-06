"""
Hierarchical configuration tool based on YAML

Reads from, in order:
- /
- install directory
- cwd()
- ~
- os.environ

Usage:

from config import settings
"""

import os
import yaml
from attrdict import AttrDict

CONFIG = 'config.yml'
INSTALL = os.path.dirname(os.path.abspath(__file__))
PWD = os.getcwd()
HOME = os.path.expanduser("~")
ROOT = '/'
PLACES = [ROOT, INSTALL, HOME, PWD]
ENVSPACE = 'TACC'
KNOWN_TYPES = ('YAML')


def yaml_to_dict(filename, permissive=True):
    """
    Safe loader for YAML files

    Positional arguments:
    filename - str - path to YAML file

    Keyword arguments:
    permissive - boolean - ignore load or parse errors

    Returns:
    An AttrDict
    """
    loaded = {}
    try:
        with open(filename, "r") as conf:
            try:
                loaded = yaml.safe_load(conf)
                if loaded is None:
                    loaded = {}
            except yaml.YAMLError as e:
                if permissive is False:
                    if hasattr(e, 'problem_mark'):
                        mark = e.problem_mark
                        raise Exception("Error {} @ line:{} col: {}".format(
                            filename, mark.line + 1, mark.column + 1))
                else:
                    pass
    except Exception as e:
        if permissive is False:
            raise Exception("YAML handling exception: {}".format(e))
        else:
            pass
    try:
        attr_loaded = AttrDict(loaded)
        return attr_loaded
    except Exception as e:
        return AttrDict({})
        pass


def variablize(keys=[], namespace=ENVSPACE):
    '''Returns config key in environment variable form'''
    if not isinstance(keys, list):
        raise TypeError("Keys must be a list")
    if len(keys) < 1 or len(keys) > 2:
        raise IndexError("Key list can only have 1 or 2 entries")
    keylist = [namespace]
    keylist.extend(keys)
    return '_'.join(keylist).upper()


def get_env_config_vals(namespace=ENVSPACE):
    '''Returns list of config values specified by env'''
    values = []
    if namespace is None:
        return values
    for n in filter(lambda k: k[0].startswith(
            namespace), os.environ.items()):
        values.append(n[1])
    return values


def read_environment(config, namespace=ENVSPACE, permissive=True):
    """
    Read in environment variable overrides

    Positional parameters:
    config - dict - a shallow copy of the main config object

    Keyword parameters:
    namespace - str - environment variable namespace. default 'TACC_'
    permissive - boolean - ignore loading or parsing errors

    Returns:
    An AttrDict configuration object
    """
    this_config = config.copy()
    for level1 in config.keys():
        if (config.get(level1) is None) or (type(config.get(level1)) is str):
            env_var = "_".join([namespace, level1]).upper()
            if os.environ.get(env_var, None) is not None:
                this_config[level1] = os.environ.get(env_var)
        elif type(config[level1]) is dict:
            for level2 in config[level1].keys():
                if (config[level1][level2] is None) or (type(config[level1][level2])) is str:
                    env_var = '_'.join([namespace, level1, level2]).upper()
                    if os.environ.get(env_var, None) is not None:
                        this_config[level1][level2] = os.environ.get(env_var)
    return this_config


def read_config(config_filename=CONFIG, places_list=PLACES, filetype='YAML',
                namespace=ENVSPACE, update=True, env=True, permissive=True):
    """
    Read in config file(s) and return an AttrDict

    Positional arguments:
    None

    Keyword arguments:
    config_filename - str - config file name. default: config.yml
    places_list - list - search path for config files. default: [/, $HOME, pwd]
    namespace - str - environment variable namespace. default 'TACC_'
    env - boolean - allow environment variable override. default: True
    permissive - boolean - ignore errors in YAML loading. default: True

    Returns:
    An AttrDict configuration object
    """

    assert filetype in KNOWN_TYPES, "{} is not a supported config file type."
    config = AttrDict()
    for p in places_list:
        fname = os.path.join(p, config_filename)
        if os.path.isfile(fname):
            this_config = yaml_to_dict(filename=fname, permissive=permissive)
            config.update(this_config)
            if update is not True:
                break

    if env is True:
        config_env = read_environment(config, namespace)
        config.update(config_env)

    return config
