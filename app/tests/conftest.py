# -*- coding: utf-8 -*-
import os
import importlib

import pytest

from src import const


@pytest.fixture
def client():
    import main
    importlib.reload(main)
    return main.app.test_client()


@pytest.fixture
def app_config():
    import main
    importlib.reload(main)
    return main.app.config


@pytest.fixture(scope='function', autouse=True)
def setup():
    os.environ[const.MONGODB_ENDPOINT] = 'mongo'
    os.environ[const.MONGODB_REPLICASET] = 'rs'
    os.environ[const.MONGODB_DATABASE] = 'db'
    os.environ[const.MONGODB_COLLECTION] = 'collection'
    os.environ[const.COMET_ENDPOINT] = 'http://comet:8666'
    os.environ[const.FIWARE_SERVICE] = 'fiware-service'
    os.environ[const.FIWARE_SERVICEPATH] = '/fiware-servicepath'
    os.environ[const.ENTITY_TYPE] = 'entity-type'
    os.environ[const.ENTITY_ID] = 'entity-id'
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
    if const.COMET_ENDPOINT in os.environ:
        del os.environ[const.COMET_ENDPOINT]
    if const.FIWARE_SERVICE in os.environ:
        del os.environ[const.FIWARE_SERVICE]
    if const.FIWARE_SERVICEPATH in os.environ:
        del os.environ[const.FIWARE_SERVICEPATH]
    if const.ENTITY_TYPE in os.environ:
        del os.environ[const.ENTITY_TYPE]
    if const.ENTITY_ID in os.environ:
        del os.environ[const.ENTITY_ID]


@pytest.fixture
def clientv2():
    os.environ[const.API_VERSION] = 'v2'
    import main
    importlib.reload(main)
    return main.app.test_client()


@pytest.fixture
def app_configv2():
    os.environ[const.API_VERSION] = 'v2'
    import main
    importlib.reload(main)
    return main.app.config


@pytest.fixture
def set_limit_as_2():
    os.environ[const.FETCH_LIMIT] = "2"
    import src.views
    importlib.reload(src.views)
    yield
    if const.FETCH_LIMIT in os.environ:
        del os.environ[const.FETCH_LIMIT]
