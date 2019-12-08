# fiware-robot-visualization
This [flask](http://flask.pocoo.org/) application visualizes the locus of [ROS](http://flask.pocoo.org/) robot.

[![Docker image size](https://img.shields.io/microbadger/image-size/nmatsui/fiware-robot-visualization.svg)](https://hub.docker.com/r/nmatsui/fiware-robot-visualization/)

## Description
This application works as a component of [FIWARE](https://www.fiware.org/).

This application retrieves a series of positions and euler angles of robot from FIWARE cygnus & STH-Comet, and visualizes it as a robot locus using d3.js.

## Requirement

**python 3.6 or higer**

## Environment Variables
This application accepts the Environment Variables like below:

|Environment Variable|Summary|Default|
|:--|:--|:--|
|`LOG_LEVEL`|log level(DEBUG, INFO, WARNING, ERRRO, CRITICAL)|INFO|
|`LISTEN_PORT`|listen port of this service|3000|
|`COMET_ENDPOINT`|the endpoint of FIWARE STH-Comet (like `http://comet:8666`)||
|`FIWARE_SERVICE`|the FIWARE SERVICE of an entity to be retrieved the historical data||
|`FIWARE_SERVICEPATH`|the FIWARE SERVICEPATH of an entity to be retrieved the historical data||
|`ENTITY_TYPE`|the entity type of an entity to be retrieved the historical data||
|`ENTITY_ID`|the entity id of an entity to be retrieved the historical data||
|`FETCH_LIMIT`|the max number to be fetch data at one time from FIWARE STH-Comet|128|

## License

[Apache License 2.0](/LICENSE)

## Copyright
Copyright (c) 2018-2019 TIS Inc.
