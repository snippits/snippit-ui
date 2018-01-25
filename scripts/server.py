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


def get_args(request):
    if request.method.decode() == 'POST':
        ret = json.loads(request.content.read().decode('utf-8'))
    elif request.method.decode() == 'GET':
        ret = {}
        for kv in request.args:
            # Solve the issue of encoding
            value = request.args[kv][0].decode('utf-8')
            try:
                ret[kv.decode('utf-8')] = float(value)
            except ValueError:
                ret[kv.decode('utf-8')] = value
            # Translate to json object
            ret = json.loads(json.dumps(ret))
    try:
        ret['similarityThreshold'] = float(ret['similarityThreshold']) / 100
    except KeyError:
        pass
    return ret


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


@app.route('/query')
@timed
def query_info(request):
    argv = get_args(request)
    ret = ''
    if argv.get('query') == 'processes':
        pids = list(processes.keys())
        pids.remove('default_')

        data = {
            'processes': sorted(pids),
            'allProcesses': sorted(pids),
        }
        ret = json.dumps(data)

    set_response_for_json(request)
    return ret


def get_timeline_middlewares(mapping_table, step_size=0):
    middlewares = []

    # Quantitize the X values if presents or not zero
    if step_size:
        middlewares += [partial(timeline.resample, quantization=step_size)]
    # Re-mapping the phase ID
    middlewares += [partial(timeline.remap, mapping_table=mapping_table)]

    return middlewares


# NOTE: process_id is defined as string. It could be a pid '748' or a name like 'testProgram'
@app.route('/phase/timeline', defaults={'process_id': None})
@app.route('/process/<process_id>/phase/timeline')
@timed
def get_phase_timeline(request, process_id):
    argv = get_args(request)
    process_id = process_id or 'default_'
    perspective = argv.get('timePerspective', 'host')
    step_size = argv.get('quantization', {'host': 10.0, 'guest': 1.0}[perspective])

    timeline_ret = []
    if process_id == 'all':
        for pid, proc in processes.items():
            if pid == 'default_': continue    # Skip this one
            mapping_table = utils.get_phase_mapping(proc['similarityMatrix'],
                                                    argv['similarityThreshold'])
            middlewares = get_timeline_middlewares(mapping_table, step_size)
            timeline_ret += [utils.apply_middleware(middlewares, proc['timeline'][perspective])]
    else:
        proc = processes[process_id]
        mapping_table = utils.get_phase_mapping(proc['similarityMatrix'],
                                                argv['similarityThreshold'])
        middlewares = get_timeline_middlewares(mapping_table, step_size)
        timeline_ret = utils.apply_middleware(middlewares, proc['timeline'][perspective])
    set_response_for_json(request)
    return json.dumps(timeline_ret)


@app.route('/phase/<int:phase_id>/treemap', defaults={'process_id': None})
@app.route('/process/<process_id>/phase/<int:phase_id>/treemap')
@timed
def get_phase_treemap(request, process_id, phase_id):
    argv = get_args(request)
    process_id = process_id or 'default_'    # set process_id to default
    proc = processes[process_id]
    # Create new phase list according to the inputs
    mapping_table = utils.get_phase_mapping(proc['similarityMatrix'], argv['similarityThreshold'])

    middlewares = [
        partial(phase.remap, mapping_table=mapping_table),
        partial(lambda phase_list: phase_list[phase_id]['codes']),
        partial(treemap.parse),
    ]

    treemap_ret = utils.apply_middleware(middlewares, proc['phases'])
    set_response_for_json(request)
    return json.dumps(treemap_ret)


@app.route('/phase/<int:phase_id>/prof', defaults={'process_id': None})
@app.route('/process/<process_id>/phase/<int:phase_id>/prof')
@timed
def get_phase_prof(request, process_id, phase_id):
    argv = get_args(request)
    process_id = process_id or 'default_'    # set process_id to default
    proc = processes[process_id]
    # Create new phase list according to the inputs
    mapping_table = utils.get_phase_mapping(proc['similarityMatrix'], argv['similarityThreshold'])

    middlewares = [
        partial(phase.remap, mapping_table=mapping_table),
        partial(lambda phase_list: phase_list[phase_id]['counters']),
    ]

    counters = utils.apply_middleware(middlewares, proc['phases'])
    set_response_for_json(request)
    return json.dumps(counters)


@app.route('/phase/<int:phase_id>/codes', defaults={'process_id': None, 'query': None})
@app.route('/phase/<int:phase_id>/codes/<query>', defaults={'process_id': None})
@app.route('/process/<process_id>/phase/<int:phase_id>/codes', defaults={'query': None})
@app.route('/process/<process_id>/phase/<int:phase_id>/codes/<query>')
@timed
def get_phase_code(request, process_id, phase_id, query):
    argv = get_args(request)
    process_id = process_id or 'default_'    # set process_id to default
    query = query or 'rawData'    # set query to default
    proc = processes[process_id]
    # Create new phase list according to the inputs
    mapping_table = utils.get_phase_mapping(proc['similarityMatrix'], argv['similarityThreshold'])

    middlewares = [
        partial(phase.remap, mapping_table=mapping_table),
        partial(lambda phase_list: phase_list[phase_id]['codes']),
    ]

    codes = utils.apply_middleware(middlewares, proc['phases'])
    retValue = {}
    if query == 'rawData':
        # Nothing to do, simply return the raw data
        retValue = codes
    elif query == 'files':
        file_list = set()
        for code in codes:
            file_list.add(''.join(code['line'].split(':')[:-1]))
        # Discard empty string if present
        file_list.discard('')
        retValue = list(file_list)
    set_response_for_json(request)
    return json.dumps(retValue)


@app.route('/host/file')
def get_host_file(request):
    argv = get_args(request)
    file_path = argv['filePath']

    retValue = []
    try:
        with open(file_path, 'r') as f:
            retValue = [''] + f.read().splitlines()
    except IOError:
        if file_path:    # If it's a valid value and not empty string
            logger.error('Unable to open file "{}"'.format(file_path))
    set_response_for_json(request)
    return json.dumps(retValue)


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
