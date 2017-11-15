# Copyright (c) 2017, Medicine Yeh

import os
import sys
import json

import numpy as np

from modules import code
from myutils.utils import CustomJSONDecoder
from myutils.utils import Hashable


def load_phase(path):
    phase_path = path + '/phases'
    with open(phase_path) as json_data:
        return json.load(json_data, cls=CustomJSONDecoder, list_type=Hashable)
    return {}


def load_timeline(path):
    phase_path = path + '/timeline'

    with open(phase_path) as json_data:
        data = json.load(json_data, cls=CustomJSONDecoder)
        return {
            'host': Hashable(list(zip(data['phases']['hostTime'], data['phases']['phaseID']))),
            'guest': Hashable(list(zip(data['phases']['guestTime'], data['phases']['phaseID'])))
        }
    return {}


def load_event(path):
    phase_path = path + '/timeline'

    with open(phase_path) as json_data:
        data = json.load(json_data, cls=CustomJSONDecoder)
        try:
            return {
                'host': Hashable(list(zip(data['events']['hostTime'], data['events']['phaseID']))),
                'guest': Hashable(list(zip(data['events']['guestTime'], data['events']['phaseID'])))
            }
        except KeyError:
            # events is an optional value here
            return {}
    return {}


def load_similarity_matrix(path):
    phase_path = path + '/phase_similarity_matrix'
    with open(phase_path) as json_data:
        return json.load(json_data)
    return {}


def _interp_time(kv):
    return [kv[0] / 1000.0, kv[1]]


def load(proc_path):
    ret_dict = {}
    for dirname in sorted(os.listdir(proc_path)):
        phase_path = os.path.join(proc_path, dirname)
        print('Found process \'{}\''.format(phase_path))

        phase_result = load_phase(phase_path)
        ret_dict[str(dirname)] = {
            'apiVersion': phase_result['apiVersion'],
            'phases': phase_result['phases'],
            'timeline': load_timeline(phase_path),
            'event': load_event(phase_path),
            'similarityMatrix': Hashable(np.asarray(load_similarity_matrix(phase_path))),
        }
        # Post-processing the input data
        process = ret_dict[str(dirname)]
        # Resolve the pathes
        if process['phases']:
            code.resolve_path(process['phases'])
            file_list = code.parse_file_list(process['phases'])
            process['workDirs'] = code.locate_working_directory(file_list)
        # Interpret value '0' as null and translate the unit on X-axis to mili-second
        if process['timeline']:
            process['timeline']['host'] = Hashable(map(_interp_time, process['timeline']['host']))
            process['timeline']['guest'] = Hashable(map(_interp_time, process['timeline']['guest']))
        # Interpret value '0' as null and translate the unit on X-axis to mili-second
        if process['event']:
            process['event']['host'] = Hashable(map(_interp_time, process['event']['host']))
            process['event']['guest'] = Hashable(map(_interp_time, process['event']['guest']))
        # Remember the first inserted one as the default
        if ret_dict.get('default_') is None:
            ret_dict['default_'] = process
    return ret_dict
