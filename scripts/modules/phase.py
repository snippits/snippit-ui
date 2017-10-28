# Copyright (c) 2017, Medicine Yeh

import json
import copy
from functools import lru_cache

from myutils import utils


def _fix_counter_value(o):
    b = o['branch']
    b['accuracy'] = b['hit'] / (b['hit'] + b['miss'])

    c = o['cache']['dCache']
    c['missRate'] = (c['readMiss'] + c['writeMiss']) / c['accessCount']
    c = o['cache']['iCache']
    c['missRate'] = (c['readMiss'] + c['writeMiss']) / c['accessCount']
    c = o['cache']['level2']
    if c:
        c['missRate'] = (c['readMiss'] + c['writeMiss']) / c['accessCount']


def merge_phase_to(target_p, source_p):
    # Do nothing if target is source
    if target_p is source_p: return target_p
    # Append the list of codes
    target_p['codes'] += source_p['codes']
    # Accumulate the number of windows
    target_p['numWidows'] += source_p['numWidows']
    # Accumulate the performance counters
    utils.deepupdate(target_p['counters'], source_p['counters'])
    # Fix the calculated values, i.e., miss rate, accuracy, etc.
    _fix_counter_value(target_p['counters'])
    return target_p


@lru_cache(maxsize=32)
def remap(phases, mapping_table):
    # Make a copy for the output
    phases_ret = copy.deepcopy(phases)
    # Loop through all phases and update itself to its target phase
    for source_p in phases_ret:
        target_id = mapping_table[source_p['id']]
        merge_phase_to(phases_ret[target_id], source_p)

    return phases_ret
