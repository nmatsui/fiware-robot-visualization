# -*- coding: utf-8 -*-
import os

import pytest

from src import const


@pytest.fixture
def client():
    import main
    return main.app.test_client()


@pytest.fixture
def app_config():
    import main
    return main.app.config


@pytest.fixture(scope='function', autouse=True)
def setup():
    os.environ[const.MONGODB_ENDPOINT] = 'mongo'
    os.environ[const.MONGODB_REPLICASET] = 'rs'
    os.environ[const.MONGODB_DATABASE] = 'db'
    os.environ[const.MONGODB_COLLECTION] = 'collection'
    yield


@pytest.fixture(scope='function', autouse=True)
def teardown():
    yield
    if const.MONGODB_ENDPOINT in os.environ:
        del os.environ[const.MONGODB_ENDPOINT]
    if const.MONGODB_REPLICASET in os.environ:
        del os.environ[const.MONGODB_REPLICASET]
    if const.MONGODB_DATABASE in os.environ:
        del os.environ[const.MONGODB_DATABASE]
    if const.MONGODB_COLLECTION in os.environ:
        del os.environ[const.MONGODB_COLLECTION]
