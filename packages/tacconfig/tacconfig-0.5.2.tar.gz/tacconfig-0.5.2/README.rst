=========
TACConfig
=========

.. image:: https://badge.fury.io/py/tacconfig.svg
    :target: http://badge.fury.io/py/tacconfig

.. image:: https://travis-ci.org/TACC/tacconfig.svg?branch=master
    :target: https://travis-ci.org/TACC/tacconfig

.. image:: https://readthedocs.org/projects/tacconfig/badge/?version=latest
    :target: https://readthedocs.org/projects/tacconfig/?badge=latest

.. image:: https://img.shields.io/pypi/l/Django.svg
    :target: https://raw.githubusercontent.com/TACC/tacconfig/master/LICENSE

**Hierarchical, YAML-based configuration for containers, web apps, and web services**

- Documentation: https://tacconfig.readthedocs.io/en/latest/
- GitHub: https://github.com/TACC/tacconfig
- PyPI: https://pypi.python.org/pypi/tacconfig
- Free software: 3-Clause BSD License

Usage
=====

.. code-block:: python

    from tacconfig import config
    settings = config.read_config(place_list, config_filename, namespace,
                                  update, env, permissive)

* ``place_list`` is the search path. Default: ``['/', cwd(), $HOME]``.
* ``config_filename`` is the name of your application config [``config.yml``]
* ``namespace`` is the prefix for override environment variables. Default: ``TACC``
* ``update`` is a Boolean. Default: ``True``. Return a synthesis of all members of search path, otherwise, returns only the first encountered.
* ``permissive`` is a Boolean. Default: ``True``. Ignore YAML errors.
* ``env`` is a Boolean. Default: ``True``. Allow specially-named environment variables to override settings.

Example
^^^^^^^

Given two config files and an environment override as follows:

.. code-block:: yaml

    ---
    # /config.yml
    logs:
        level: "INFO"

.. code-block:: yaml

    ---
    # /home/tacobot/config.yml
    logs:
        level: "DEBUG"

.. code-block:: shell

    $ export TACC_LOGS_LEVEL="WARNING"

.. code-block:: python

    #/usr/bin/env python

    from tacconfig import config

    settings = config.read_config()

In the code block above, the value of ``settings.logs.level`` will be
``"WARNING"``. If one unsets the environment variable ``TACC_LOGS_LEVEL``,
``settings.logs.level`` will be ``"DEBUG"``. If one deletes or renames
``/home/tacobot/config.yml``, ``settings.logs.level`` will be ``INFO``.

Also note that, in keeping with this modules expected usage as a configuration
management tool, ``settings`` can be navigated using dot notation.

Tests
=====

Tests are implemented using tox_. To run them, just type ``tox``

.. _tox: https://tox.readthedocs.io/en/latest
