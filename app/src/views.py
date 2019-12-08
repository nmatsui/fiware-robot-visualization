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
        positions_path = url_for(RobotPositionsAPIBase.NAME)
        return render_template('robotLocus.html', path=positions_path)


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

        for attrName in ('y'):
            for attr in self.__send_request_to_comet(attrName, start_dt, end_dt):
                recv_time = attr['recvTime']
                if recv_time in points:
                    points[recv_time][attrName] = float(attr['attrValue'])

        return jsonify(list(points.values()))

    def __send_request_to_comet(self, attr, start_dt, end_dt):
        logger.debug(f'get "{attr}" from {start_dt} to {end_dt}')
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

        current_num = 0
        result = list()

        while True:
            params = {
                'hLimit': RobotPositionsAPIv2.FETCH_LIMIT,
                'hOffset': current_num,
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
                logger.debug(f'total-count of {attr} = {count}')
                if count == 0:
                    continue
            except (ValueError, TypeError) as e:
                logger.error(f'invalid fiware-total-count, fiware-total-count={response.get("fiware-total-count")}'
                             f'error={str(e)}')
                return []

            result.extend(response.json()["contextResponses"][0]["contextElement"]["attributes"][0]["values"])
            logger.debug(f'result length of {attr} = {len(result)}')

            current_num += RobotPositionsAPIv2.FETCH_LIMIT
            logger.debug(f'next fetch count of {attr} = {current_num}')
            if current_num >= count:
                break

        logger.info(f'retrieve {len(result)} data, entity_type={RobotPositionsAPIv2.ENTITY_TYPE}, '
                     f'entity_id={RobotPositionsAPIv2.ENTITY_ID}, attr={attr}, start_dt={start_dt}, end_dt={end_dt}')
        return result
