# -*- coding: utf-8 -*-
import os
from collections import OrderedDict

from logging import getLogger

from dateutil import parser
from pytz import timezone

from pymongo import MongoClient, ASCENDING

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
                                          *url_for(RobotPositionsAPI.NAME).split(os.sep)[1:])
        else:
            positions_path = url_for(RobotPositionsAPI.NAME)

        prefix = os.environ[const.PREFIX] if const.PREFIX in os.environ else ''

        return render_template('robotLocus.html', bearer=bearer, path=positions_path, prefix=prefix)


class RobotPositionsAPI(MethodView):
    NAME = 'robot_positions_api'

    ENDPOINT = os.environ[const.MONGODB_ENDPOINT]
    REPLICASET = os.environ[const.MONGODB_REPLICASET]
    DB = os.environ[const.MONGODB_DATABASE]
    COLLECTION = os.environ[const.MONGODB_COLLECTION]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if const.CYGNUS_MONGO_ATTR_PERSISTENCE in os.environ and os.environ[const.CYGNUS_MONGO_ATTR_PERSISTENCE] == 'row':
            self.is_row = True
        else:
            self.is_row = False

    def get(self):
        st = request.args.get('st')
        et = request.args.get('et')

        tz = current_app.config['TIMEZONE']

        logger.info(f'RobotPositionAPI, st={st} et={et}')
        if not st or not et:
            raise BadRequest({'message': 'empty query parameter "st" and/or "et"'})

        try:
            start_dt = parser.parse(st).astimezone(timezone(tz))
            end_dt = parser.parse(et).astimezone(timezone(tz))
        except (TypeError, ValueError):
            raise BadRequest({'message': 'invalid query parameter "st" and/or "et"'})

        client = MongoClient(RobotPositionsAPI.ENDPOINT, replicaset=RobotPositionsAPI.REPLICASET)
        collection = client[RobotPositionsAPI.DB][RobotPositionsAPI.COLLECTION]

        points = OrderedDict()
        if self.is_row:
            for attr in collection.find({"recvTime": {"$gte": start_dt, "$lt": end_dt}}).sort([("recvTime", ASCENDING)]):
                recv_time = attr['recvTime']
                if recv_time not in points:
                    d = dict()
                    d['time'] = recv_time.astimezone(timezone(tz)).isoformat()
                    points[recv_time] = d
                if attr['attrName'] in ['x', 'y', 'z', 'theta']:
                    points[recv_time][attr['attrName']] = float(attr['attrValue'])
        else:
            for attr in collection.find({"recvTime": {"$gte": start_dt, "$lt": end_dt}}).sort([("recvTime", ASCENDING)]):
                recv_time = attr['recvTime']
                d = {k: attr[k] for k in ('x', 'y', 'z', 'theta') if k in attr}
                d['time'] = recv_time.astimezone(timezone(tz)).isoformat()
                points[recv_time] = d

        return jsonify(list(points.values()))
