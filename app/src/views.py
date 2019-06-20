# -*- coding: utf-8 -*-
import os
from collections import OrderedDict
from urllib.parse import urljoin

from logging import getLogger

from dateutil import parser
from pytz import timezone

from pymongo import MongoClient, ASCENDING

import requests

from flask import request, render_template, jsonify, current_app, url_for
from flask.views import MethodView
from werkzeug.exceptions import BadRequest

from src import const

logger = getLogger(__name__)


class RobotLocusPage(MethodView):
    NAME = 'robot_locus_page'

    def get(self):
        if const.BEARER_AUTH in os.environ:
            bearer = os.environ[const.BEARER_AUTH]
        else:
            bearer = current_app.config[const.DEFAULT_BEARER_AUTH]

        if const.PREFIX in os.environ:
            positions_path = os.path.join('/',
                                          os.environ.get(const.PREFIX, '').strip(),
                                          *url_for(RobotPositionsAPIBase.NAME).split(os.sep)[1:])
        else:
            positions_path = url_for(RobotPositionsAPIBase.NAME)

        prefix = os.environ[const.PREFIX] if const.PREFIX in os.environ else ''

        return render_template('robotLocus.html', bearer=bearer, path=positions_path, prefix=prefix)


class RobotPositionsAPIBase(MethodView):
    NAME = 'robot_positions_api'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tz = timezone(current_app.config['TIMEZONE'])

    def _parse_params(self):
        st = request.args.get('st')
        et = request.args.get('et')

        logger.info(f'RobotPositionAPI, st={st} et={et}')
        if not st or not et:
            raise BadRequest({'message': 'empty query parameter "st" and/or "et"'})

        try:
            start_dt = parser.parse(st).astimezone(self.tz)
            end_dt = parser.parse(et).astimezone(self.tz)
        except (TypeError, ValueError):
            raise BadRequest({'message': 'invalid query parameter "st" and/or "et"'})

        return start_dt, end_dt


class RobotPositionsAPI(RobotPositionsAPIBase):
    ENDPOINT = os.environ.get(const.MONGODB_ENDPOINT)
    REPLICASET = os.environ.get(const.MONGODB_REPLICASET)
    DB = os.environ.get(const.MONGODB_DATABASE)
    COLLECTION = os.environ.get(const.MONGODB_COLLECTION)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if const.CYGNUS_MONGO_ATTR_PERSISTENCE in os.environ and os.environ[const.CYGNUS_MONGO_ATTR_PERSISTENCE] == 'row':
            self.is_row = True
        else:
            self.is_row = False

    def get(self):
        start_dt, end_dt = super()._parse_params()
        client = MongoClient(RobotPositionsAPI.ENDPOINT, replicaset=RobotPositionsAPI.REPLICASET)
        collection = client[RobotPositionsAPI.DB][RobotPositionsAPI.COLLECTION]

        points = OrderedDict()
        if self.is_row:
            for attr in collection.find({"recvTime": {"$gte": start_dt, "$lt": end_dt}}).sort([("recvTime", ASCENDING)]):
                recv_time = attr['recvTime']
                if recv_time not in points:
                    d = dict()
                    d['time'] = recv_time.astimezone(self.tz).isoformat()
                    points[recv_time] = d
                if attr['attrName'] in ['x', 'y', 'z', 'theta']:
                    points[recv_time][attr['attrName']] = float(attr['attrValue'])
        else:
            for attr in collection.find({"recvTime": {"$gte": start_dt, "$lt": end_dt}}).sort([("recvTime", ASCENDING)]):
                recv_time = attr['recvTime']
                d = {k: attr[k] for k in ('x', 'y', 'z', 'theta') if k in attr}
                d['time'] = recv_time.astimezone(self.tz).isoformat()
                points[recv_time] = d

        return jsonify(list(points.values()))


class RobotPositionsAPIv2(RobotPositionsAPIBase):
    ENDPOINT = os.environ.get(const.COMET_ENDPOINT)
    FIWARE_SERVICE = os.environ.get(const.FIWARE_SERVICE)
    FIWARE_SERVICEPATH = os.environ.get(const.FIWARE_SERVICEPATH)
    ENTITY_TYPE = os.environ.get(const.ENTITY_TYPE)
    ENTITY_ID = os.environ.get(const.ENTITY_ID)
    FETCH_LIMIT = int(os.environ.get(const.FETCH_LIMIT, const.DEFAULT_FETCH_LIMIT))

    def get(self):
        start_dt, end_dt = [dt.isoformat() for dt in super()._parse_params()]

        points = OrderedDict()
        for attr in self.__send_request_to_comet('x', start_dt, end_dt):
            recv_time = attr['recvTime']
            if recv_time not in points:
                points[recv_time] = {'time': parser.parse(recv_time).astimezone(self.tz).isoformat()}
            points[recv_time]['x'] = float(attr['attrValue'])

        for attrName in ('y', 'z', 'theta'):
            for attr in self.__send_request_to_comet(attrName, start_dt, end_dt):
                recv_time = attr['recvTime']
                if recv_time in points:
                    points[recv_time][attrName] = float(attr['attrValue'])

        return jsonify(list(points.values()))

    def __send_request_to_comet(self, attr, start_dt, end_dt):
        headers = dict()
        headers['Fiware-Service'] = RobotPositionsAPIv2.FIWARE_SERVICE
        headers['Fiware-Servicepath'] = RobotPositionsAPIv2.FIWARE_SERVICEPATH

        path = os.path.join(const.BASE_PATH,
                            "type",
                            RobotPositionsAPIv2.ENTITY_TYPE,
                            "id",
                            RobotPositionsAPIv2.ENTITY_ID,
                            "attributes",
                            attr)
        endpoint = urljoin(RobotPositionsAPIv2.ENDPOINT, path)

        current_page = 0
        result = list()

        while True:
            params = {
                'hLimit': RobotPositionsAPIv2.FETCH_LIMIT,
                'hOffset': current_page,
                'dateFrom': start_dt,
                'dateTo': end_dt,
                'count': 'true',
            }

            response = requests.get(endpoint, headers=headers, params=params)

            if response.status_code != 200:
                logger.error(f'can not retrieve data from sth-coment, status_code={response.status_code}, '
                             f'data={response.text}')
                return []
            try:
                count = int(response.headers.get('fiware-total-count', '0'))
            except (ValueError, TypeError) as e:
                logger.error(f'invalid fiware-total-count, fiware-total-count={response.get("fiware-total-count")}'
                             f'error={str(e)}')
                return []

            result.extend(response.json()["contextResponses"][0]["contextElement"]["attributes"][0]["values"])

            current_page += RobotPositionsAPIv2.FETCH_LIMIT
            if current_page >= count:
                break

        logger.debug(f'retrieve {len(result)} data, entity_type={RobotPositionsAPIv2.ENTITY_TYPE}, '
                     f'entity_id={RobotPositionsAPIv2.ENTITY_ID}, attr={attr}, start_dt={start_dt}, end_dt={end_dt}')
        return result
