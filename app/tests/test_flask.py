# -*- coding: utf-8 -*-
import os

from dateutil import parser
from pytz import timezone

from pymongo import ASCENDING

import pytest
from pyquery import PyQuery as pq

from src import const


class TestRobotLocusPage:

    def test_head(self, client):
        response = client.head('/locus')
        assert response.status_code == 301
        assert not hasattr(response, 'body')
        assert response.headers['Location'].endswith('/locus/')

        response = client.head('/locus/')
        assert response.status_code == 200
        assert not hasattr(response, 'body')

    @pytest.mark.parametrize(('bearer', 'p_value', 'p_expected'), [
        (None, None, '/positions/'),
        ('', '', '/positions/'),
        ('bearer', '/', '/positions/'),
        ('bearer', 'foo', '/foo/positions/'),
        ('bearer', '/foo', '/foo/positions/'),
        ('bearer', '/foo/', '/foo/positions/'),
    ])
    def test_get(self, client, app_config, bearer, p_value, p_expected):
        if bearer is not None:
            os.environ[const.BEARER_AUTH] = bearer
        if p_value is not None:
            os.environ[const.PREFIX] = p_value

        response = client.get('/locus')
        assert response.status_code == 301
        assert not hasattr(response, 'body')
        assert response.headers['Location'].endswith('/locus/')

        response = client.get('/locus/')
        assert response.status_code == 200
        assert response.content_type == 'text/html; charset=utf-8'
        q = pq(response.data.decode('utf-8'), parser='html')

        assert q.find('title').text() == 'Robot Visualization'
        assert len(q.find('h3.text-muted')) == 1
        assert q.find('h3.text-muted').text() == 'Robot Locus'
        assert len(q.find('input.datetimepicker-input#st_datetime_value[type="text"][data-target="#st_datetime"]')) == 1
        assert len(q.find('div.input-group-append[data-target="#st_datetime"][data-toggle="datetimepicker"]')) == 1
        assert len(q.find('input.datetimepicker-input#et_datetime_value[type="text"][data-target="#et_datetime"]')) == 1
        assert len(q.find('div.input-group-append[data-target="#et_datetime"][data-toggle="datetimepicker"]')) == 1
        assert len(q.find('div#not_rendering button#show_button[disabled="disabled"]')) == 1
        assert len(q.find('div#not_rendering button#clear_button')) == 1
        assert len(q.find('div#rendering[style="display: none;"] button#stop_button')) == 1
        assert len(q.find('svg#robotLocus')) == 1
        assert len(q.find('div#point_num')) == 1
        assert q.find('div#point_num').text() == ''
        assert len(q.find('div#time')) == 1
        assert q.find('div#time').text() == ''
        assert len(q.find('div#pos_x')) == 1
        assert q.find('div#pos_x').text() == ''
        assert len(q.find('div#pos_y')) == 1
        assert q.find('div#pos_y').text() == ''
        assert len(q.find('div#pos_theta')) == 1
        assert q.find('div#pos_theta').text() == ''

        assert len(q.find('input#bearer[type="hidden"]')) == 1
        if bearer is not None:
            assert q.find('input#bearer[type="hidden"]').val() == bearer
        else:
            assert q.find('input#bearer[type="hidden"]').val() == app_config[const.DEFAULT_BEARER_AUTH]
        assert len(q.find('input#path[type="hidden"]')) == 1
        assert q.find('input#path[type="hidden"]').val() == p_expected

        if const.BEARER_AUTH in os.environ:
            del os.environ[const.BEARER_AUTH]
        if const.PREFIX in os.environ:
            del os.environ[const.PREFIX]

    @pytest.mark.parametrize('method', ['post', 'put', 'patch', 'delete'])
    @pytest.mark.parametrize('path', ['/locus', '/locus/'])
    def test_method_not_allowed(self, client, method, path):
        response = getattr(client, method)(path)
        assert response.status_code == 405
        assert not hasattr(response, 'body')


class TestRobotPositionsAPI:

    def test_head(self, client):
        response = client.head('/positions')
        assert response.status_code == 301
        assert not hasattr(response, 'body')
        assert response.headers['Location'].endswith('/positions/')

        response = client.head('/positions/')
        assert response.status_code == 400
        assert not hasattr(response, 'body')

    def test_get_success_row(self, mocker, client, app_config):
        os.environ[const.CYGNUS_MONGO_ATTR_PERSISTENCE] = "row"

        response = client.get('/positions')
        assert response.status_code == 301
        assert not hasattr(response, 'body')
        assert response.headers['Location'].endswith('/positions/')

        st = '2018-01-02T03:04:05+09:00'
        et = '2018-01-06T03:04:05+09:00'
        recv_time_0 = '2018-01-03T03:04:05+09:00'
        recv_time_1 = '2018-01-04T03:04:05+09:00'
        recv_time_2 = '2018-01-05T03:04:05+09:00'

        params = {
            'st': st,
            'et': et,
        }
        tz = app_config['TIMEZONE']

        mocked_MongoClient = mocker.patch('src.views.MongoClient')
        mocked_client = mocked_MongoClient.return_value
        mocked_collection = mocked_client.__getitem__.return_value.__getitem__.return_value

        recvTime0 = parser.parse(recv_time_0)
        recvTime1 = parser.parse(recv_time_1)
        recvTime2 = parser.parse(recv_time_2)
        mocked_collection.find.return_value.sort.return_value = [
            {
                'recvTime': recvTime0,
                'attrName': 'x',
                'attrValue': 0.0,
            }, {
                'recvTime': recvTime0,
                'attrName': 'y',
                'attrValue': 0.1,
            }, {
                'recvTime': recvTime0,
                'attrName': 'z',
                'attrValue': 0.2,
            }, {
                'recvTime': recvTime0,
                'attrName': 'theta',
                'attrValue': 0.3,
            }, {
                'recvTime': recvTime0,
                'attrName': 'dummy',
                'attrValue': 'dummy0',
            }, {
                'recvTime': recvTime1,
                'attrName': 'dummy',
                'attrValue': 'dummy1',
            }, {
                'recvTime': recvTime2,
                'attrName': 'x',
                'attrValue': 2.0,
            }, {
                'recvTime': recvTime2,
                'attrName': 'y',
                'attrValue': 2.1,
            },
        ]

        response = client.get('/positions/', query_string=params)

        mocked_MongoClient.assert_called_once_with('mongo', replicaset='rs')
        mocked_client.return_value.assert_not_called
        mocked_client.__getitem__.assert_called_once_with('db')
        mocked_client.__getitem__.return_value.__getitem__.assert_called_once_with('collection')
        mocked_collection.find.assert_called_once_with({
            "recvTime": {
                "$gte": parser.parse(st).astimezone(timezone(tz)),
                "$lt": parser.parse(et).astimezone(timezone(tz)),
            }
        })
        mocked_collection.find.return_value.sort.assert_called_once_with([("recvTime", ASCENDING)])

        assert response.status_code == 200
        assert response.content_type == 'application/json'

        expected = [
            {
                'time': recv_time_0,
                'x': 0.0,
                'y': 0.1,
                'z': 0.2,
                'theta': 0.3,
            }, {
                'time': recv_time_1,
            }, {
                'time': recv_time_2,
                'x': 2.0,
                'y': 2.1,
            }
        ]
        assert response.json == expected

        if const.CYGNUS_MONGO_ATTR_PERSISTENCE in os.environ:
            del os.environ[const.CYGNUS_MONGO_ATTR_PERSISTENCE]

    @pytest.mark.parametrize('env', ['None', '', 'column', 'dummy'])
    def test_get_success_column(self, mocker, client, app_config, env):
        if env != 'None':
            os.environ[const.CYGNUS_MONGO_ATTR_PERSISTENCE] = env

        response = client.get('/positions')
        assert response.status_code == 301
        assert not hasattr(response, 'body')
        assert response.headers['Location'].endswith('/positions/')

        st = '2018-01-02T03:04:05+09:00'
        et = '2018-01-06T03:04:05+09:00'
        recv_time_0 = '2018-01-03T03:04:05+09:00'
        recv_time_1 = '2018-01-04T03:04:05+09:00'
        recv_time_2 = '2018-01-05T03:04:05+09:00'

        params = {
            'st': st,
            'et': et,
        }
        tz = app_config['TIMEZONE']

        mocked_MongoClient = mocker.patch('src.views.MongoClient')
        mocked_client = mocked_MongoClient.return_value
        mocked_collection = mocked_client.__getitem__.return_value.__getitem__.return_value

        recvTime0 = parser.parse(recv_time_0)
        recvTime1 = parser.parse(recv_time_1)
        recvTime2 = parser.parse(recv_time_2)
        mocked_collection.find.return_value.sort.return_value = [
            {
                'recvTime': recvTime0,
                'x': 0.0,
                'y': 0.1,
                'z': 0.2,
                'theta': 0.3,
            }, {
                'recvTime': recvTime1,
                'dummy': 'dummy',
            }, {
                'recvTime': recvTime2,
                'x': 2.0,
                'y': 2.1,
            },
        ]

        response = client.get('/positions/', query_string=params)

        mocked_MongoClient.assert_called_once_with('mongo', replicaset='rs')
        mocked_client.return_value.assert_not_called
        mocked_client.__getitem__.assert_called_once_with('db')
        mocked_client.__getitem__.return_value.__getitem__.assert_called_once_with('collection')
        mocked_collection.find.assert_called_once_with({
            "recvTime": {
                "$gte": parser.parse(st).astimezone(timezone(tz)),
                "$lt": parser.parse(et).astimezone(timezone(tz)),
            }
        })
        mocked_collection.find.return_value.sort.assert_called_once_with([("recvTime", ASCENDING)])

        assert response.status_code == 200
        assert response.content_type == 'application/json'

        expected = [
            {
                'time': recv_time_0,
                'x': 0.0,
                'y': 0.1,
                'z': 0.2,
                'theta': 0.3,
            }, {
                'time': recv_time_1,
            }, {
                'time': recv_time_2,
                'x': 2.0,
                'y': 2.1,
            }
        ]
        assert response.json == expected

        if const.CYGNUS_MONGO_ATTR_PERSISTENCE in os.environ:
            del os.environ[const.CYGNUS_MONGO_ATTR_PERSISTENCE]

    def test_get_no_param(self, mocker, client):
        mocked_MongoClient = mocker.patch('src.views.MongoClient')
        mocked_client = mocked_MongoClient.return_value
        mocked_collection = mocked_client.__getitem__.return_value.__getitem__.return_value

        response = client.get('/positions/')

        mocked_MongoClient.assert_not_called
        mocked_client.return_value.assert_not_called
        mocked_client.__getitem__.assert_not_called
        mocked_client.__getitem__.return_value.__getitem__.assert_not_called
        mocked_collection.find.assert_not_called
        mocked_collection.find.return_value.sort.assert_not_called

        assert response.status_code == 400
        assert not hasattr(response, 'body')

    @pytest.mark.parametrize('st', [None, '', 'dummy'])
    @pytest.mark.parametrize('et', [None, '', 'dummy'])
    def test_get_invalid_params(self, mocker, client, st, et):
        params = {}
        if st is not None:
            params['st'] = st
        if et is not None:
            params['et'] = et

        mocked_MongoClient = mocker.patch('src.views.MongoClient')
        mocked_client = mocked_MongoClient.return_value
        mocked_collection = mocked_client.__getitem__.return_value.__getitem__.return_value

        response = client.get('/positions/', query_string=params)

        mocked_MongoClient.assert_not_called
        mocked_client.return_value.assert_not_called
        mocked_client.__getitem__.assert_not_called
        mocked_client.__getitem__.return_value.__getitem__.assert_not_called
        mocked_collection.find.assert_not_called
        mocked_collection.find.return_value.sort.assert_not_called

        assert response.status_code == 400
        assert not hasattr(response, 'body')

    @pytest.mark.parametrize('method', ['post', 'put', 'patch', 'delete'])
    @pytest.mark.parametrize('path', ['/locus', '/locus/'])
    def test_method_not_allowed(self, client, method, path):
        response = getattr(client, method)(path)
        assert response.status_code == 405
        assert not hasattr(response, 'body')


class TestNotFound:

    @pytest.mark.parametrize('method', ['get', 'post', 'put', 'patch', 'delete', 'head'])
    @pytest.mark.parametrize('path', ['/invalid/', '/invalid', ])
    def test_not_found(self, client, method, path):
        response = getattr(client, method)(path)
        assert response.status_code == 404
        assert not hasattr(response, 'body')
