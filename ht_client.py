#!/usr/bin/python

import json
import logging
import requests
from time import sleep
import argparse
from jinja2 import Environment, FileSystemLoader
import matplotlib.pyplot as plt

logging.basicConfig(filename='/tmp/dht_client.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

NUM_OF_SAMPLES = 20
# Better to set high interval to ensure we don't overload the sensor.
SLEEP_INTERVAL = 30 # Seconds
HTML_TEMPLATE = None


def main_args():
    args = get_args()
    run(args.address, args.port, args.samples, args.interval)


def get_args():
    parser = argparse.ArgumentParser(
        description=(
            'Service to query a servcer running ht_server service and' +
            ' generate an HTML report of the results.'
        )
    )
    parser.add_argument(
        'address', type=str, help='Address of the server'
    )
    parser.add_argument(
        'port', type=int, help='Port to connect through to the server'
    )
    parser.add_argument(
        '--interval', type=int, default=SLEEP_INTERVAL,
        help='Interval between queries (seconds). Default={}'.format(
            SLEEP_INTERVAL)
    )
    parser.add_argument(
        '--samples', type=int, default=NUM_OF_SAMPLES,
        help='Interval between queries. Default={}'.format(NUM_OF_SAMPLES)
    )
    return parser.parse_args()


def run(address, port, samples, sleep_interval):
    logger.info(
        'Beginning queries session.' +
        ' Address %s, Port %s, Samples %s, Interval %s',
        address, port, samples, sleep_interval)
    set_global_jinja_template()
    time_samples = []
    humidity_samples = []
    temperature_samples = []
    for sample in xrange(0, NUM_OF_SAMPLES):
        data = get_data_from_server(address, port)
        logger.info('Sample %s/%s::data from server: %s',
                    sample+1, NUM_OF_SAMPLES, data)
        time = data.get('time')
        humidity = data.get('humidity')
        temperature = data.get('temperature')
        time_samples.append(time)
        print("Time: {} Humidity: {} Temperature: {}").format(time, humidity,
                                                              temperature)
        humidity_samples.append(humidity)
        temperature_samples.append(temperature)
        if(sample > 1):
            make_graph_image(humidity_samples, temperature_samples)
            render_jinja_template(sample, temperature, humidity)
        sleep(sleep_interval)


def make_graph_image(humidity, temperature):
    samples = range(0,len(humidity))
    fig = plt.figure(1)
    plt.plot(samples, humidity, label="Humidity", color='g')
    plt.plot(samples, temperature, label="Temperature", color='r')
    plt.grid(True)
    # plt.show()
    fig.savefig('foo.png')
    plt.close()


def render_jinja_template(num_of_samples, last_temp, last_humi):
    HTML_TEMPLATE.stream(
        num_of_samples=num_of_samples,
        last_temp=last_temp,
        last_humi=last_humi
    ).dump('view.html')


def set_global_jinja_template():
    global HTML_TEMPLATE
    env = Environment(loader=FileSystemLoader('templates/'))
    HTML_TEMPLATE = env.get_template('basic_view.html')


def get_data_from_server(server_url='localhost', port=4000):
    headers = {'content-type': 'serv/json'}
    payload = {
        'method': 'read_dht_sensor',
        'params': [],
        'jsonrpc': '2.0',
        'id': 0
    }
    url = 'http://{url}:{port}/jsonrpc'.format(url=server_url, port=port)
    response = requests.post(
        url, data=json.dumps(payload), headers=headers
    ).json()
    return response.get('result')


if __name__ == '__main__':
    main_args()
    #main()
