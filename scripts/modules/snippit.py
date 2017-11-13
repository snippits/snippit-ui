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


def load_similarity_matrix(path):
    phase_path = path + '/phase_similarity_matrix'
    with open(phase_path) as json_data:
        return json.load(json_data)
    return {}


def _mask_zero(kv):
    return [kv[0] / 1000.0, kv[1]]


def load(proc_path):
    ret_dict = {}
    for dirname in sorted(os.listdir(proc_path)):
        phase_path = os.path.join(proc_path, dirname)
        print('Found process \'{}\''.format(phase_path))
        ret_dict[str(dirname)] = {
            'info': load_phase(phase_path),
            'timeline': load_timeline(phase_path),
            'similarityMatrix': Hashable(np.asarray(load_similarity_matrix(phase_path))),
        }
        process = ret_dict[str(dirname)]
        if process['info']:
            code.resolve_path(process['info']['phase'])
            file_list = code.parse_file_list(process['info']['phase'])
            process['workDirs'] = code.locate_working_directory(file_list)
        if process['timeline']:
            process['timeline']['host'] = Hashable(map(_mask_zero, process['timeline']['host']))
            process['timeline']['guest'] = Hashable(map(_mask_zero, process['timeline']['guest']))
        ret_dict['default_'] = process    # remember the last inserted one as default
    return ret_dict
