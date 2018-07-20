# -*- coding: utf-8 -*-

from flask import render_template
from flask.views import MethodView


class RobotLocusPage(MethodView):
    NAME = 'robot_locus_page'

    def get(self):
        return render_template('robotLocus.html')
