# -*- coding: utf-8 -*-
import os

from dateutil import parser
import pytz

import pytest
from pyquery import PyQuery as pq

from src import const


class TestRobotLocusPage:

    def test_head(self, client):
        response = client.head('/locus')
        assert response.status_code in (301, 308)
        assert not hasattr(response, 'body')
        assert response.headers['Location'].endswith('/locus/')

        response = client.head('/locus/')
        assert response.status_code == 200
        assert not hasattr(response, 'body')

    def test_get(self, client, app_config):
        response = client.get('/locus')
        assert response.status_code in (301, 308)
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

        assert len(q.find('input#path[type="hidden"]')) == 1
        assert q.find('input#path[type="hidden"]').val() == '/positions/'

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


class TestNotFound:

    @pytest.mark.parametrize('method', ['get', 'post', 'put', 'patch', 'delete', 'head'])
    @pytest.mark.parametrize('path', ['/invalid/', '/invalid', ])
    def test_not_found(self, client, method, path):
        response = getattr(client, method)(path)
        assert response.status_code == 404
        assert not hasattr(response, 'body')


class TestRobotPositionsAPIv2:

    def __get_json(self, params):
        values = list()
        for recvTime, attrValue in params:
            values.append({
                'recvTime': recvTime,
                'attrType': 'float',
                'attrValue': attrValue,
            })

        return {
            'contextResponses': [
                {
                    'contextElement': {
                        'attributes': [
                            {
                                'values': values,
                            }
                        ]
                    }
                }
            ]
        }

    def test_head(self, clientv2):
        response = clientv2.head('/positions')
        assert response.status_code in (301, 308)
        assert not hasattr(response, 'body')
        assert response.headers['Location'].endswith('/positions/')

        response = clientv2.head('/positions/')
        assert response.status_code == 400
        assert not hasattr(response, 'body')

    @pytest.mark.parametrize('headers', [{'fiware-total-count': '5'}])
    def test_get_success_wo_loop(self, requests_mock, clientv2, app_config, headers):
        response = clientv2.get('/positions')
        assert response.status_code in (301, 308)
        assert not hasattr(response, 'body')
        assert response.headers['Location'].endswith('/positions/')

        st = '2018-01-02T03:04:05+09:00'
        et = '2018-01-08T03:04:05+09:00'
        recv_time_0 = '2018-01-03T03:04:05+09:00'
        recv_time_1 = '2018-01-04T03:04:05+09:00'
        recv_time_2 = '2018-01-05T03:04:05+09:00'
        recv_time_3 = '2018-01-06T03:04:05+09:00'
        recv_time_4 = '2018-01-07T03:04:05+09:00'

        params = {
            'st': st,
            'et': et,
        }
        recvTime0 = parser.parse(recv_time_0).astimezone(pytz.UTC).isoformat()
        recvTime1 = parser.parse(recv_time_1).astimezone(pytz.UTC).isoformat()
        recvTime2 = parser.parse(recv_time_2).astimezone(pytz.UTC).isoformat()
        recvTime3 = parser.parse(recv_time_3).astimezone(pytz.UTC).isoformat()
        recvTime4 = parser.parse(recv_time_4).astimezone(pytz.UTC).isoformat()

        vx = self.__get_json([
            (recvTime0, 0.0), (recvTime1, 0.1), (recvTime2, 0.2), (recvTime3, 0.3), (recvTime4, 0.4)
        ])
        vy = self.__get_json([
            (recvTime0, 1.0), (recvTime1, 1.1), (recvTime2, 1.2), (recvTime3, 1.3), (recvTime4, 1.4)
        ])

        urlstr = 'http://comet:8666/STH/v1/contextEntities/type/entity-type/id/entity-id/attributes/'
        if headers is None:
            requests_mock.get(urlstr + 'x', json=vx)
            requests_mock.get(urlstr + 'y', json=vy)
        else:
            requests_mock.get(urlstr + 'x', json=vx, headers=headers)
            requests_mock.get(urlstr + 'y', json=vy, headers=headers)

        response = clientv2.get('/positions/', query_string=params)

        assert response.status_code == 200
        assert response.content_type == 'application/json'

        expected = [
            {
                'time': recv_time_0,
                'x': 0.0,
                'y': 1.0,
            }, {
                'time': recv_time_1,
                'x': 0.1,
                'y': 1.1,
            }, {
                'time': recv_time_2,
                'x': 0.2,
                'y': 1.2,
            }, {
                'time': recv_time_3,
                'x': 0.3,
                'y': 1.3,
            }, {
                'time': recv_time_4,
                'x': 0.4,
                'y': 1.4,
            }
        ]
        assert response.json == expected

    @pytest.mark.usefixtures('set_limit_as_2')
    @pytest.mark.parametrize('headers', [{'fiware-total-count': '2'}, {'fiware-total-count': '5'}])
    def test_get_success_w_loop(self, requests_mock, clientv2, app_config, headers):
        response = clientv2.get('/positions')
        assert response.status_code in (301, 308)
        assert not hasattr(response, 'body')
        assert response.headers['Location'].endswith('/positions/')

        st = '2018-01-02T03:04:05+09:00'
        et = '2018-01-08T03:04:05+09:00'
        recv_time_0 = '2018-01-03T03:04:05+09:00'
        recv_time_1 = '2018-01-04T03:04:05+09:00'
        recv_time_2 = '2018-01-05T03:04:05+09:00'
        recv_time_3 = '2018-01-06T03:04:05+09:00'
        recv_time_4 = '2018-01-07T03:04:05+09:00'

        params = {
            'st': st,
            'et': et,
        }
        recvTime0 = parser.parse(recv_time_0).astimezone(pytz.UTC).isoformat()
        recvTime1 = parser.parse(recv_time_1).astimezone(pytz.UTC).isoformat()
        recvTime2 = parser.parse(recv_time_2).astimezone(pytz.UTC).isoformat()
        recvTime3 = parser.parse(recv_time_3).astimezone(pytz.UTC).isoformat()
        recvTime4 = parser.parse(recv_time_4).astimezone(pytz.UTC).isoformat()

        vx1 = self.__get_json([(recvTime0, 0.0), (recvTime1, 0.1)])
        vx2 = self.__get_json([(recvTime2, 0.2), (recvTime3, 0.3)])
        vx3 = self.__get_json([(recvTime4, 0.4)])
        vy1 = self.__get_json([(recvTime0, 1.0), (recvTime1, 1.1)])
        vy2 = self.__get_json([(recvTime2, 1.2), (recvTime3, 1.3)])
        vy3 = self.__get_json([(recvTime4, 1.4)])

        urlstr = 'http://comet:8666/STH/v1/contextEntities/type/entity-type/id/entity-id/attributes/'
        if headers is None:
            requests_mock.get(urlstr + 'x', [{'json': vx1}, {'json': vx2}, {'json': vx3}])
            requests_mock.get(urlstr + 'y', [{'json': vy1}, {'json': vy2}, {'json': vy3}])
        else:
            requests_mock.get(urlstr + 'x', [
                {'json': vx1, 'headers': headers},
                {'json': vx2, 'headers': headers},
                {'json': vx3, 'headers': headers}
            ])
            requests_mock.get(urlstr + 'y', [
                {'json': vy1, 'headers': headers},
                {'json': vy2, 'headers': headers},
                {'json': vy3, 'headers': headers}
            ])

        response = clientv2.get('/positions/', query_string=params)

        assert response.status_code == 200
        assert response.content_type == 'application/json'

        base_expected = [
            {
                'time': recv_time_0,
                'x': 0.0,
                'y': 1.0,
            }, {
                'time': recv_time_1,
                'x': 0.1,
                'y': 1.1,
            }
        ]
        extended_expected = base_expected + [
            {
                'time': recv_time_2,
                'x': 0.2,
                'y': 1.2,
            }, {
                'time': recv_time_3,
                'x': 0.3,
                'y': 1.3,
            }, {
                'time': recv_time_4,
                'x': 0.4,
                'y': 1.4,
            }
        ]
        if headers is not None and headers['fiware-total-count'] == '5':
            assert response.json == extended_expected
        else:
            assert response.json == base_expected

    def test_get_no_param(self, requests_mock, clientv2):
        response = clientv2.get('/positions/')

        urlstr = 'http://comet:8666/STH/v1/contextEntities/type/entity-type/id/entity-id/attributes/'

        assert not requests_mock.get(urlstr + 'x').called
        assert not requests_mock.get(urlstr + 'y').called
        assert not requests_mock.get(urlstr + 'z').called
        assert not requests_mock.get(urlstr + 'theta').called

        assert response.status_code == 400
        assert not hasattr(response, 'body')

    @pytest.mark.parametrize('st', [None, '', 'dummy'])
    @pytest.mark.parametrize('et', [None, '', 'dummy'])
    def test_get_invalid_params(self, requests_mock, clientv2, st, et):
        params = {}
        if st is not None:
            params['st'] = st
        if et is not None:
            params['et'] = et

        response = clientv2.get('/positions/', query_string=params)

        urlstr = 'http://comet:8666/STH/v1/contextEntities/type/entity-type/id/entity-id/attributes/'
        assert not requests_mock.get(urlstr + 'x').called
        assert not requests_mock.get(urlstr + 'y').called
        assert not requests_mock.get(urlstr + 'z').called
        assert not requests_mock.get(urlstr + 'theta').called

        assert response.status_code == 400
        assert not hasattr(response, 'body')

    @pytest.mark.parametrize('method', ['post', 'put', 'patch', 'delete'])
    @pytest.mark.parametrize('path', ['/positions', '/positions/'])
    def test_method_not_allowed(self, clientv2, method, path):
        response = getattr(clientv2, method)(path)
        assert response.status_code == 405
        assert not hasattr(response, 'body')
