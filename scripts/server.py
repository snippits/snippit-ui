#!/usr/bin/env python3
# Copyright (c) 2017, Medicine Yeh

import os
import sys
import getopt
import glob
import json

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import textwrap

from flask import Flask, request, send_from_directory, send_file

BASE_PATH = os.path.dirname(os.path.realpath(__file__))
PARENTDIR = os.path.dirname(BASE_PATH)

STATIC_DIR = os.path.join(BASE_PATH, '..', 'public')
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 5000

def parsePhase(path):
    phase_path = path + '/phases'
    with open(phase_path) as json_data:
        return json.load(json_data)
    return {}

def parsePhases(proc_path):
    ret_dict = {}
    for dirname in os.listdir(proc_path):
        phase_path = os.path.join(proc_path, dirname)
        print('Found process \'' + phase_path + '\'')
        ret_dict[str(dirname)] = {'info': parsePhase(phase_path)}
        ret_dict['default_'] = ret_dict[str(dirname)] # remember the last inserted one as default
    return ret_dict

# set the project root directory as the static folder
app = Flask(__name__)

@app.route('/')
def root():
    path = os.path.join(STATIC_DIR, 'index.html')
    return send_file(path, cache_timeout=0)

@app.route('/<path:path>')
def static_file(path):
    return send_from_directory(STATIC_DIR, path, cache_timeout=0)

@app.route('/phase/<int:phase_id>/prof', methods=['POST'])
def get_phase_prof(phase_id):
    info = phase_info['default_']['info'];
    # Use the last element as default
    response = app.response_class(
        response=json.dumps(info['phase'][phase_id]['counters']),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/phase/<int:phase_id>/codes', methods=['POST'])
def get_phase_code(phase_id):
    info = phase_info['default_']['info'];
    # Use the last element as default
    response = app.response_class(
        response=json.dumps(info['phase'][phase_id]['codes']),
        status=200,
        mimetype='application/json'
    )
    return response

def get_descriptions():
    return textwrap.dedent('''\
    A webserver for snippits UI web interface.
    ''')

def get_sample_usage():
    return textwrap.dedent('''\
    Sample Usage:
            Ex: server.py -i /tmp/snippit
    ''')

def main(argv):
    ap = ArgumentParser('server.py',
            formatter_class=RawDescriptionHelpFormatter,
            description=get_descriptions(),
            epilog=get_sample_usage())
    ap.add_argument('--input', '-i', help='Input Directory', type=str, default='/tmp/snippit')
    ap.add_argument('--host', help='The host ip address on which Snippit webserver serve. ' \
            'Defaults to' + DEFAULT_HOST, type=str, default=DEFAULT_HOST)
    ap.add_argument('--port', '-p', help='The port on which Snippit webserver will be hosted. ' \
            'Defaults to' + str(DEFAULT_PORT), type=int, default=DEFAULT_PORT)
    args = ap.parse_args()

    input_path = os.path.abspath(args.input)
    proc_path = os.path.join(input_path, 'proc')

    global phase_info;
    phase_info = parsePhases(proc_path);

    app.run(host=DEFAULT_HOST, port=DEFAULT_PORT)

if __name__ == '__main__':
    main(sys.argv[1:])
