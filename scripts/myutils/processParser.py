import os
import sys
import json

def parsePhase(path):
    phase_path = path + '/phases'
    with open(phase_path) as json_data:
        return json.load(json_data)
    return {}

def parseSimilarityMatrix(path):
    phase_path = path + '/phase_similarity_matrix'
    with open(phase_path) as json_data:
        return json.load(json_data)
    return {}

def parseAllProcesses(proc_path):
    ret_dict = {}
    for dirname in os.listdir(proc_path):
        phase_path = os.path.join(proc_path, dirname)
        print('Found process \'{}\''.format(phase_path))
        ret_dict[str(dirname)] = {
                    'info': parsePhase(phase_path),
                    'similarityMatrix': parseSimilarityMatrix(phase_path),
                }
        ret_dict['default_'] = ret_dict[str(dirname)] # remember the last inserted one as default
    return ret_dict
