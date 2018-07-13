#!/usr/bin/python

import logging
import json
from time import time
from uuid import uuid4
from jsonrpc import JSONRPCResponseManager, dispatcher
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from Adafruit_DHT import read as dht_read


logging.basicConfig(filename='/tmp/dht_server.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)


@dispatcher.add_method
def read_dht_sensor(dht_sensor_type=11, gpio_pin=4):
    """
    read data from dht sensor of type $dht_sensor_type on gpio pin number
    $gpio_pin.

    :param dth_sensor_type: Version of DHT sensor.
                            Default: 11
    :param int gpio_pin:    Num of GPIO pin the DHT-11 sensor is connected at.
                            Default: 4

    :rtype: dict
    :returns: dictionary with the temperature, humidity and the time of the
              reading.
    """
    logger.debug(
        'Attempt to read data from sensor type [%s] on pin [%s]',
        dht_sensor_type, gpio_pin
    )
    read_time = time()
    humi, temp = dht_read(dht_sensor_type, gpio_pin)
    data = {
        'humidity': humi,
        'temperature': temp,
        'time': read_time,
        'key': str(uuid4())
    }
    if not humi or not temp:
        logger.error(
            'Attempt to read data from sensor type [%s] on pin [%s] FAILED!',
            dht_sensor_type, gpio_pin
        )
    logger.info('Data constructed: %s', data)
    return data


@Request.application
def serv(request):
    """
    A simple server utility that handles HTTP POST requests and passes them
    to JSONRPCResponseManager. The requst should include on of the sensor
    providers.

        'method': '$SENSOR_PROVIDER',
        'params': [],
        'jsonrpc': '2.0',
        'id': 0

    """
    response = JSONRPCResponseManager.handle(request.data, dispatcher)
    return Response(response.json, mimetype='serv/json')


if __name__ == '__main__':
    run_simple('localhost', 4000, serv)
