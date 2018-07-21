# -*- coding: utf-8 -*-
import os
import math

from logging import getLogger

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

    def get(self):
        st = request.args.get('st')
        et = request.args.get('et')

        logger.info(f'RobotPositionAPI, st={st} et={et}')
        if not st or not et:
            raise BadRequest({'message': 'empty query parameter "st" and/or "et"'})

        dummy_data = []
        for i in range(32 + 1):
            dummy_data.append({
                'x': math.cos(i * math.pi / 16.0),
                'y': math.sin(i * math.pi / 16.0),
                'z': 0.0,
                'theta': 0.0,
            })

        return jsonify(dummy_data)
