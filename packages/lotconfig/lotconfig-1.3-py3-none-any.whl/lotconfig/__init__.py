#!/usr/bin/env python3

import logging
import copy

import dpath.util
import yaml
import sys
import os
import re
from weakref import proxy

RE_EVAL = re.compile(r'^\s*eval\s*\((?P<expression>[^\)]+)\)\s*$').match

logger = logging.getLogger(__name__)

class Config(object):
    """ Load configuration from a yaml file.

    But this does a few extra special things, too:

    1. Mode detection
    2. Key references
    3. Python expression evaluations.

    More on those special features below.

    In order to load a config from a file, say::

        config = Config.load('/path/to/config.yaml')

    You can also specify a field you're using for ``mode`` (see "Mode
    detection" below).
        ::

        config = Config.load('/path/to/config', mode_keyword='environment').

    In this way if you have 'environment' as a key in the root level,
    whatever ``environment`` is set to will be the mode.

    Since a configuration is heirarchical, you can refer to configuration
    values by a path:

        config['server/port']

    If the path isn't valid, it will simply return None.

    Mode detection
    ==============

    There's a default keyword you can specify at the beginning of the file
    to specify a mode. For example::

        mode: development

    This mode can be used throughout the file to specify different
    environments. For the mode value, prefix it with '@' (and make sure
    to surround it with quotes, since YAML does't like '@' for keys).
    For example:

        server:
            '@development':
                host: localhost
                port: 5000
            '@production':
                host: example.com
                port: 5000

    This way, whenever ``mode`` is ``'production'``, you can refer ``server``
    will automatically refer to ``{host: "example.com", "port": 5000}``, and if
    mode is set to ``developemnt``, then ``server`` will refer to
    ``{host: "localhost", "port": 5000}``.

    **IMPORTANT.** These mode keys are essentially invisible. You can't
    force the configuation to read ``config['server/@development/host.']``.

    So if mode is ``production`` ``config['server/host']`` is ``example.com``.
    If mode is ``development`` ``config['server/host']`` is ``localhost``.

    Key References
    ==============

    Don't repeat yourself. You can refer to another value within the config
    using a key reference. Key references are strings that refer to other
    config values.

    References are preceded with a tilde (``~``).

    """

    def __init__(self, args=(), kwargs={}, mode_keyword=None,
                 environment={}, seperator='/', _path=None):
        self.mode_keyword = mode_keyword
        self._path = _path
        self._env = environment
        self._sep = seperator
        self._store = dict(*args, **kwargs[kwargs[mode_keyword]])

    def __contains__(self, key):
        try:
            dpath.util.get(self._store, key)
            return True
        except KeyError as e:
            return False
        return False

    def __delitem__(self, key):
        return dpath.util.delete(self._store, key, seperator=self._sep)

    def __eq__(self, value):
        return isinstance(value, type(self)) and (self._store == value._store)

    def __ge__(self, value):
        return self >= value

    def as_dict(self, normalized=True):
        """ Get the configuration as a dictionary.

        :param normalized: Return the normalizd dictionary (with refrences,
            modes, and evals removed.)
        """
        if normalized:
            return self._normalized
        return self._store

    def get(self, key, default=None):
        """ Get an item from the configuration based on the key.

        :param key: Path for the configuration value.

        :param default: Default value to return if `key` isn't found.
        """
        try:
            return dpath.util.get(self._store, key, self._sep)
        except KeyError as e:
            return default

    def set(self, key, value):
        dpath.util.set(self._store, key, value, self._sep)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value, True)

    def get_fail(self, key):
        """ A not-so-nice fetch method that throws KeyError on not found. """
        if self.__getitem__(key) is None:
            raise KeyError('{} not found in config {}'.format(key, self._path))
        return self.__getitem__(key)

    @property
    def mode(self):
        if not self.mode_keyword:
            return None
        else:
            try:
                return dpath.util.get(self._store, self.mode_keyword)
            except KeyError as e:
                return None

    def items(self):
        for (k, v) in self._store.items():
            if (self.mode and isinstance(v, dict)
                and ('@' + self.mode) in v):
                yield (k, v['@' + self.mode])
            else:
                yield (k, v)

    def __gt__(self, value):
        return (isinstance(value), type(self)) and self._store > value._store

    def __iter__(self):
        return self._store.__iter__()

    def __le__(self, value):
        return (isinstance(value), type(self)) and self < value

    def __len__(self):
        return (isinstance(value), type(self)) and len(self._store)

    def __lt__(self, value):
        return (isinstance(value), type(self)) and self._store < value._store

    def __ne__ (self, value):
        return (isinstance(value), type(self)) or self._store != value._store

    def __str__(self):
        return str(self._store)

    @classmethod
    def load(cls, path, mode_keyword='mode', expanduser=True,
             abspath=True, seperator='/'):
        """ Load configuration from a path.

        :param path: Path to the configuration file.

        :param mode_keyword: Keyword to use for the mode. Can be a full path,
            too (e.g. '/path/to/mode').

        :param expand_user: Whether the path supplied should expand '~'
            Default is True

        :param abspath: Should the path resolve to an absolue path. Default is
            True

        :param seperator: Path seperator for the config. Default is '/'

        :return: Config object loaded from `path`

        :raise: ValueError if path is not found or no data is in configuration.
        """

        if abspath:
            path = os.path.abspath(path)
        if expanduser:
            path = os.path.expanduser(path)
        with open(path, 'r') as f:
            data = yaml.load(f)
            if data is None:
                raise ValueError('No data found in {}'.format(path))
            return cls(kwargs=data, mode_keyword='mode',
                       _path=path, seperator=seperator)

    @classmethod
    def load_or_create(cls, path, mode_keyword='mode', expanduser=True,
                       abspath=True, seperator='/'):
        """ Load a configuration, if it exists.
        Otherwise, create a new config and load that.

        Signature is the same for `Config.load`
        """
        if abspath:
            path = os.path.abspath(path)
        if expanduser:
            path = os.path.expanduser(path)
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        kwargs = dict(mode_keyword=mode_keyword,
                      expanduser=expanduser,
                      abspath=abspath,
                      seperator=seperator)
        if os.path.exists(path):
            return cls.load(path, **kwargs)
        config = cls(_path=path, mode_keyword=mode_keyword, seperator=seperator)
        config.write()
        return config

    def write_stream(self, stream):
        yaml.dump(self._store, stream)

    def write(self, path=None, mode='w+', create_dirs=True):
        path = os.path.abspath(self._path or path or '')
        d = os.path.dirname(path)
        if not os.path.exists(d) and create_dirs:
            os.path.makedirs(d)
        with open(path, mode) as f:
            self.write_stream(f)
