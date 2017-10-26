# Copyright (c) 2017, Medicine Yeh

import os
import sys
import json


def load_phase(path):
    phase_path = path + '/phases'
    with open(phase_path) as json_data:
        return json.load(json_data)
    return {}


def load_similarity_matrix(path):
    phase_path = path + '/phase_similarity_matrix'
    with open(phase_path) as json_data:
        return json.load(json_data)
    return {}


def load(proc_path):
    ret_dict = {}
    for dirname in os.listdir(proc_path):
        phase_path = os.path.join(proc_path, dirname)
        print('Found process \'{}\''.format(phase_path))
        ret_dict[str(dirname)] = {
            'info': load_phase(phase_path),
            'similarityMatrix': load_similarity_matrix(phase_path),
        }
        ret_dict['default_'] = ret_dict[str(dirname)]    # remember the last inserted one as default
    return ret_dict
