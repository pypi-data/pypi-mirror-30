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
ENVSPACE = '''TACC'''


def yaml_to_dict(filename, permissive=True):

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


def read_config(places_list=PLACES, config_filename=CONFIG,
                namespace=ENVSPACE, update=True, env=True, permissive=True):

    config = AttrDict()
    for p in places_list:
        fname = os.path.join(p, config_filename)
        if os.path.isfile(fname):
            this_config = yaml_to_dict(filename=fname, permissive=permissive)
            config.update(this_config)
            if update is not True:
                break

    if env is True:
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
        if config != this_config:
            config.update(this_config)

    return config


settings = read_config()
