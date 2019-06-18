#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import logging.config
from logging import getLogger

from flask import Flask

from src.views import RobotLocusPage, RobotPositionsAPI, RobotPositionsAPIv2
from src import error_handler
from src import const

try:
    with open(const.LOGGING_JSON, "r") as f:
        logging.config.dictConfig(json.load(f))
        if (const.LOG_LEVEL in os.environ and
                os.environ[const.LOG_LEVEL].upper() in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']):
            for handler in getLogger().handlers:
                if handler.get_name() in const.TARGET_HANDLERS:
                    handler.setLevel(getattr(logging, os.environ[const.LOG_LEVEL].upper()))
except FileNotFoundError:
    pass


app = Flask(__name__)
app.config.from_pyfile(const.CONFIG_CFG)
app.add_url_rule('/locus/', view_func=RobotLocusPage.as_view(RobotLocusPage.NAME))

if os.environ.get(const.API_VERSION, '') == 'v2':
    app.add_url_rule('/positions/', view_func=RobotPositionsAPIv2.as_view(RobotPositionsAPI.NAME))
else:
    app.add_url_rule('/positions/', view_func=RobotPositionsAPI.as_view(RobotPositionsAPI.NAME))
app.register_blueprint(error_handler.blueprint)


if __name__ == '__main__':
    default_port = app.config[const.DEFAULT_PORT]
    try:
        port = int(os.environ.get(const.LISTEN_PORT, str(default_port)))
        if port < 1 or 65535 < port:
            port = default_port
    except ValueError:
        port = default_port

    app.run(host="0.0.0.0", port=port)
