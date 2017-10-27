#!/usr/bin/env python3
# Copyright (c) 2017, Medicine Yeh

import os
import sys
import getopt
import glob
import json
import time
import textwrap
import logging
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from functools import partial

# Third party
import flask
import flask_profiler
import logzero
from logzero import logger

# Modules for this project
from modules import snippit
from modules import timeline
from modules import phase
from modules import treemap
from modules import code
# Other utilities of this project
from myutils import bcolors
from myutils import utils
from myutils.decorators import timed

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
PARENTDIR = os.path.dirname(BASE_PATH)

STATIC_DIR = os.path.join(BASE_PATH, '..', 'public')
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 5000
DEFAULT_INPUT_PATH = '/tmp/snippit'

processes = []

# Set the project root directory as the static folder
app = flask.Flask(__name__)

# Load settings
app.config.from_object('flask_config.DefaultConfig')
if os.environ.get('SNIPPIT_UI_CONFIG'):
    app.config.from_envvar('SNIPPIT_UI_CONFIG')

# Necessary configuration to initialize flask-profiler:
app.config['flask_profiler'] = {
    'enabled': app.config['DEBUG'],
    'storage': {
        'engine': 'sqlite'
    },
    'basicAuth': {
        'enabled': True,
        'username': 'admin',
        'password': 'admin'
    },
    'ignore': []
}


def get_similarity_params(request):
    requestValues = request.get_json(silent=True)
    sim_mat = processes['default_']['similarityMatrix']
    if requestValues['similarityThreshold']:
        sim_thold = float(requestValues['similarityThreshold']) / 100.0
    else:
        sim_thold = None

    return (sim_mat, sim_thold)


@app.route('/')
def root():
    path = os.path.join(STATIC_DIR, 'index.html')
    return flask.send_file(path, cache_timeout=0)


@app.route('/<path:path>')
def static_file(path):
    return flask.send_from_directory(STATIC_DIR, path, cache_timeout=0)


@app.route('/phase/timeline', methods=['POST'])
@timed
def get_phase_timeline():
    info = processes['default_']['info']
    (sim_mat, sim_thold) = get_similarity_params(flask.request)
    # Get mapping table for remapping the timeline to its new phase ID
    mapping_table = utils.get_phase_mapping(sim_mat, sim_thold)

    from modules.timeline import Event
    middlewares = [
        partial(timeline.remap, mapping_table=mapping_table),
        partial(timeline.append_event, event_list=info['events'], event=Event.CONTEXT_SWITCH),
        partial(sorted),
    ]

    timeline_ret = utils.apply_middleware(middlewares, info['timeline'])
    response = app.response_class(
        response=json.dumps(timeline_ret), status=200, mimetype='application/json')
    return response


@app.route('/phase/<int:phase_id>/treemap', methods=['POST'])
@timed
def get_phase_treemap(phase_id):
    info = processes['default_']['info']
    (sim_mat, sim_thold) = get_similarity_params(flask.request)
    # Create new phase list according to the inputs
    mapping_table = utils.get_phase_mapping(sim_mat, sim_thold)

    middlewares = [
        partial(phase.remap, mapping_table=mapping_table),
        partial(lambda phase_list: phase_list[phase_id]['codes']),
        partial(treemap.parse),
    ]

    treemap_ret = utils.apply_middleware(middlewares, info['phase'])
    response = app.response_class(
        response=json.dumps(treemap_ret), status=200, mimetype='application/json')
    return response


@app.route('/phase/<int:phase_id>/prof', methods=['POST'])
@timed
def get_phase_prof(phase_id):
    info = processes['default_']['info']
    (sim_mat, sim_thold) = get_similarity_params(flask.request)
    # Create new phase list according to the inputs
    mapping_table = utils.get_phase_mapping(sim_mat, sim_thold)

    middlewares = [
        partial(phase.remap, mapping_table=mapping_table),
        partial(lambda phase_list: phase_list[phase_id]['counters']),
    ]

    counters = utils.apply_middleware(middlewares, info['phase'])
    response = app.response_class(
        response=json.dumps(counters), status=200, mimetype='application/json')
    return response


@app.route('/phase/<int:phase_id>/codes', methods=['POST'])
@timed
def get_phase_code(phase_id):
    info = processes['default_']['info']
    (sim_mat, sim_thold) = get_similarity_params(flask.request)
    # Create new phase list according to the inputs
    mapping_table = utils.get_phase_mapping(sim_mat, sim_thold)

    middlewares = [
        partial(phase.remap, mapping_table=mapping_table),
        partial(lambda phase_list: phase_list[phase_id]['codes']),
    ]

    codes = utils.apply_middleware(middlewares, info['phase'])
    response = app.response_class(
        response=json.dumps(codes), status=200, mimetype='application/json')
    return response


# In order to active flask-profiler, you have to pass flask
# app as an argument to flask-profiler.
# All the endpoints declared so far will be tracked by flask-profiler.
flask_profiler.init_app(app)


def get_descriptions():
    return textwrap.dedent('''\
    A webserver for snippits UI web interface.
    ''')


def get_sample_usage():
    return textwrap.dedent('''\
    Sample Usage:
            Ex: server.py /tmp/snippit
    ''')


def main(argv):
    ap = ArgumentParser(
        'server.py',
        formatter_class=RawDescriptionHelpFormatter,
        description=get_descriptions(),
        epilog=get_sample_usage())
    ap.add_argument(
        'input_path',
        metavar='PATH',
        type=str,
        nargs='?',
        default=DEFAULT_INPUT_PATH,
        help='The path to Snippits output. Defaults to {}'.format(DEFAULT_INPUT_PATH))
    ap.add_argument(
        '--host',
        type=str,
        default=DEFAULT_HOST,
        help='The host ip address on which Snippit webserver serve. Defaults to {}'.format(
            DEFAULT_HOST))
    ap.add_argument(
        '--port',
        '-p',
        type=int,
        default=DEFAULT_PORT,
        help='The port on which Snippit webserver will be hosted. Defaults to {}'.format(
            DEFAULT_PORT))
    args = ap.parse_args()

    input_path = os.path.abspath(args.input_path)
    proc_path = os.path.join(input_path, 'proc')
    if (os.path.exists(proc_path) == False):
        print('{} path \'{}\' not found!'.format(bcolors.WARNING_STR, proc_path))

    global processes
    processes = snippit.load(proc_path)
    if (len(processes) == 0):
        print('{} no processes found under \'{}\'!'.format(bcolors.WARNING_STR, proc_path))

    print(' * Server running on: {}http://{}:{}/{}'.format(bcolors.OKBLUE, args.host, args.port,
                                                           bcolors.ENDC))

    # Set a minimum log level
    logzero.loglevel(logging.INFO)
    if (app.config['DEBUG']):
        print(' * Profiling results on: {}http://{}:{}/flask-profiler/{}'.format(
            bcolors.OKBLUE, args.host, args.port, bcolors.ENDC))
        auth = app.config['flask_profiler']['basicAuth']
        print('       username: {}    password: {}'.format(auth['username'], auth['password']))
        logzero.loglevel(logging.DEBUG)

    if (app.config['DEBUG']):
        app.run(host=args.host, port=args.port, use_debugger=True, use_reloader=True)
    else:
        app.run(host=args.host, port=args.port)


if __name__ == '__main__':
    main(sys.argv[1:])
