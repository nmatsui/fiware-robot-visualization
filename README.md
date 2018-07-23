# fiware-robot-visualization
This [flask](http://flask.pocoo.org/) application visualizes the locus of [ROS](http://flask.pocoo.org/) robot.

## Description
This application works as a component of [FIWARE](https://www.fiware.org/).

This application retrieves a series of positions and euler angles of robot from FIWARE cygnus, and visualizes it as a robot locus using d3.js.

## Requirement

**python 3.6 or higer**

## Environment Variables
This application accepts the Environment Variables like below:

|Environment Variable|Summary|Default|
|:--|:--|:--|
|`LOG_LEVEL`|log level(DEBUG, INFO, WARNING, ERRRO, CRITICAL)|INFO|
|`LISTEN_PORT`|listen port of this service|3000|
|`PREFIX`|the prefix specified as the ambassador's annotation||
|`BEARER_AUTH`|Bearer Auth token used by ajax request||
|`MONGODB_ENDPOINT`|the endpoint of MongoDB which is used by FIWARE cygnus (like `mongodb:27017`)||
|`MONGODB_REPLICASET`|the replicaset name of MongoDB which is used by FIWARE cygnus (like `rs0`)||
|`MONGODB_DATABASE`|the database name of MongoDB which is used by FIWARE cygnus||
|`MONGODB_COLLECTION`|the collection name of MongoDB which is used by FIWARE cygnus||

## License

[Apache License 2.0](/LICENSE)

## Copyright
Copyright (c) 2018 TIS Inc.
