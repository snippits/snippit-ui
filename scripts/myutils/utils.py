# Copyright (c) 2017, Medicine Yeh

import json
from functools import lru_cache

from myutils import mapping_table


class Hashable(list):
    def __hash__(self):
        return id(self)


class CustomJSONDecoder(json.JSONDecoder):
    def __init__(self, list_type=list, **kwargs):
        json.JSONDecoder.__init__(self, **kwargs)
        # Use the custom JSONArray
        self.parse_array = self.JSONArray
        # Use the python implemenation of the scanner
        self.scan_once = json.scanner.py_make_scanner(self)
        self.list_type = list_type

    def JSONArray(self, s_and_end, scan_once, **kwargs):
        values, end = json.decoder.JSONArray(s_and_end, scan_once, **kwargs)
        return self.list_type(values), end


@lru_cache(maxsize=32)
def get_phase_mapping(sim_mat, sim_thold=1.0):
    return Hashable(mapping_table.nearest_above(sim_mat, sim_thold))


def deepupdate(target, src):
    for k, v in src.items():
        if isinstance(v, list):
            if not k in target:
                target[k] = copy.deepcopy(v)
            else:
                target[k].extend(v)
        elif isinstance(v, dict):
            if not k in target:
                target[k] = copy.deepcopy(v)
            else:
                deepupdate(target[k], v)
        elif isinstance(v, set):
            if not k in target:
                target[k] = v.copy()
            else:
                target[k].update(v.copy())
        else:
            target[k] += v
