#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import yacm

import pytest

import yacm

BASE = os.path.dirname(__file__)


def test_merge():
    # check to merge two config files
    foo = {'c': {'foo': 1}}
    cfg = {}
    yacm.merge(cfg, foo)
    assert cfg == foo

    yacm.merge(cfg, {})
    assert cfg == foo

    # configs must be dict of dicts
    with pytest.raises(AttributeError):
        yacm.merge({}, 1)

    with pytest.raises(AttributeError):
        yacm.merge({}, {'a': 1})


def test_simple():
    cfg = yacm.read_file(BASE + '/configs/simple.yml')
    assert isinstance(cfg, dict)
    assert cfg['plugins']['db'] is True

    cfg = yacm.read_file([
        BASE + '/configs/simple.yml',
        BASE + '/configs/no_rwdb.yml'
    ])
    assert cfg['plugins']['db'] is False
    assert cfg['plugins']['someother_db'] is True

    cfg = yacm.read_file([
        BASE + '/configs/no_rwdb.yml',
        BASE + '/configs/simple.yml',
    ])
    assert cfg['plugins']['db'] is True
    assert cfg['plugins']['someother_db'] is True


def test_config_paths():
    """when inside a virtualenv we are looking for more configs"""
    env = os.environ.get('VIRTUAL_ENV')
    if env is not None:
        del os.environ['VIRTUAL_ENV']
    configs = yacm.get_config_paths('rw')
    os.environ['VIRTUAL_ENV'] = '/tmp'
    configs_ve = yacm.get_config_paths('rw')
    if env is None:
        del os.environ['VIRTUAL_ENV']
    else:
        os.environ['VIRTUAL_ENV'] = env

    assert len(configs) < len(configs_ve)
