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
import klein
import logzero
from logzero import logger
from twisted.web.static import File

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
DEFAULT_INPUT_PATH = '/tmp/snippit'

processes = []

# Set the project root directory as the static folder
app = klein.Klein()

# Load settings
setattr(app, 'config', {
    'DEBUG': False,
    'HOST': '127.0.0.1',
    'PORT': 5000,
})

# Set a minimum log level
logzero.loglevel(logging.INFO)
# Set up debug mode settings
if os.environ.get('DEBUG'):
    app.config['DEBUG'] = True
    logzero.loglevel(logging.DEBUG)


def klein_args_get(request, key, default=None):
    ret = None
    if request.method.decode() == 'POST':
        args = json.loads(request.content.read())
        ret = args.get(key, default)
    elif request.method.decode() == 'GET':
        ret = request.args.get(byte(key), [default])[0]
    return ret


def get_args(request):
    sim_thold = klein_args_get(request, 'similarityThreshold')

    if sim_thold is not None:
        sim_thold = float(sim_thold) / 100.0

    return (sim_thold)


def get_params(proc_id=None):
    if proc_id is not None:
        info = processes[proc_id]['info']
        process_timeline = processes[proc_id]['timeline']
        sim_mat = processes[proc_id]['similarityMatrix']
    else:
        info = processes['default_']['info']
        process_timeline = processes['default_']['timeline']
        sim_mat = processes['default_']['similarityMatrix']
    return (info, process_timeline, sim_mat)


def set_response_for_json(request):
    request.setHeader('Content-Type', 'application/json')
    request.setHeader('Cache-Control', 'no-store')


@app.route("/", branch=True)
def static_file(request):
    request.setHeader('Cache-Control', 'no-cache')
    return File(STATIC_DIR)


@app.route("/index.html")
def index(request):
    request.setHeader('Cache-Control', 'no-cache')
    return File(os.path.join(STATIC_DIR, 'index.html'))


@app.route('/phase/timeline', methods=['POST', 'GET'])
@timed
def get_phase_timeline(request):
    (info, process_timeline, sim_mat) = get_params()
    (sim_thold) = get_args(request)
    # Get mapping table for remapping the timeline to its new phase ID
    mapping_table = utils.get_phase_mapping(sim_mat, sim_thold)

    from modules.timeline import Event
    middlewares = [
        partial(timeline.remap, mapping_table=mapping_table),
    #partial(timeline.append_event, event_list=info['events'], event=Event.CONTEXT_SWITCH),
    #partial(sorted),
    ]

    timeline_ret = utils.apply_middleware(middlewares, process_timeline['timeline'])
    set_response_for_json(request)
    return json.dumps(timeline_ret)


@app.route('/phase/<int:phase_id>/treemap', methods=['POST'])
@timed
def get_phase_treemap(request, phase_id):
    (info, process_timeline, sim_mat) = get_params()
    (sim_thold) = get_args(request)
    # Create new phase list according to the inputs
    mapping_table = utils.get_phase_mapping(sim_mat, sim_thold)

    middlewares = [
        partial(phase.remap, mapping_table=mapping_table),
        partial(lambda phase_list: phase_list[phase_id]['codes']),
        partial(treemap.parse),
    ]

    treemap_ret = utils.apply_middleware(middlewares, info['phase'])
    set_response_for_json(request)
    return json.dumps(treemap_ret)


@app.route('/phase/<int:phase_id>/prof', methods=['POST'])
@timed
def get_phase_prof(request, phase_id):
    (info, process_timeline, sim_mat) = get_params()
    (sim_thold) = get_args(request)
    # Create new phase list according to the inputs
    mapping_table = utils.get_phase_mapping(sim_mat, sim_thold)

    middlewares = [
        partial(phase.remap, mapping_table=mapping_table),
        partial(lambda phase_list: phase_list[phase_id]['counters']),
    ]

    counters = utils.apply_middleware(middlewares, info['phase'])
    set_response_for_json(request)
    return json.dumps(counters)


@app.route('/phase/<int:phase_id>/codes', methods=['POST'])
@timed
def get_phase_code(request, phase_id):
    (info, process_timeline, sim_mat) = get_params()
    (sim_thold) = get_args(request)
    # Create new phase list according to the inputs
    mapping_table = utils.get_phase_mapping(sim_mat, sim_thold)

    middlewares = [
        partial(phase.remap, mapping_table=mapping_table),
        partial(lambda phase_list: phase_list[phase_id]['codes']),
    ]

    codes = utils.apply_middleware(middlewares, info['phase'])
    set_response_for_json(request)
    return json.dumps(codes)


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
        help='The path to Snippits output which contains profiling counters. '
        'Defaults to {}'.format(DEFAULT_INPUT_PATH))
    ap.add_argument(
        '--host',
        type=str,
        default=app.config['HOST'],
        help='The host ip address on which Snippit webserver serve. '
        'Defaults to {}'.format(app.config['HOST']))
    ap.add_argument(
        '--port',
        '-p',
        type=int,
        default=app.config['PORT'],
        help='The port on which Snippit webserver will be hosted. '
        'Defaults to {}'.format(app.config['PORT']))
    args = ap.parse_args()

    input_path = os.path.abspath(args.input_path)
    proc_path = os.path.join(input_path, 'proc')
    if os.path.exists(proc_path) == False:
        print('{} path \'{}\' not found!'.format(bcolors.WARNING_STR, proc_path))

    global processes
    processes = snippit.load(proc_path)
    if len(processes) == 0:
        print('{} no processes found under \'{}\'!'.format(bcolors.WARNING_STR, proc_path))

    print(' * Server running on: '
          '{}http://{}:{}/{}'.format(bcolors.OKBLUE, args.host, args.port, bcolors.ENDC))

    app.run(host=args.host, port=args.port)


if __name__ == '__main__':
    main(sys.argv[1:])
