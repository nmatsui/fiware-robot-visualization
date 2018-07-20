# -*- coding: utf-8 -*-
import math

from logging import getLogger

from flask import request, render_template, jsonify
from flask.views import MethodView
from werkzeug.exceptions import BadRequest

logger = getLogger(__name__)


class RobotLocusPage(MethodView):
    NAME = 'robot_locus_page'

    def get(self):
        return render_template('robotLocus.html')


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
