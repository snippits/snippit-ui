# Copyright (c) 2017, Medicine Yeh
import copy

import myutils.createMappingTable as createMappingTable
from . import utils

cached_mappingTable = {}
cached_simTh = 0
cached_simMat = {}
def getPhaseMappingTable(simMat, simTh):
    global cached_mappingTable, cached_simTh
    if (simMat is cached_simMat and simTh == cached_simTh):
        return cached_mappingTable

    cached_mappingTable = createMappingTable.nearestAbove(simMat, simTh)

    return cached_mappingTable

def reCalculateValues(o):
    b = o['branch']
    b['accuracy'] = b['hit'] / (b['hit'] + b['miss'])

    c = o['cache']['dCache']
    c['missRate'] = (c['readMiss'] + c['writeMiss']) / c['accessCount']
    c = o['cache']['iCache']
    c['missRate'] = (c['readMiss'] + c['writeMiss']) / c['accessCount']
    c = o['cache']['level2']
    if (c):
        c['missRate'] = (c['readMiss'] + c['writeMiss']) / c['accessCount']

def getMergedPhases(phases, simMat, simTh):
    # Get mapping table and remap the timeline to its new phase ID
    mappingTable = getPhaseMappingTable(simMat, simTh)
    output_phases = copy.deepcopy(phases)
    for p in output_phases:
        m = mappingTable[p['id']]
        if (p['id'] == m): continue
        o = output_phases[m]
        o['codes'] += p['codes']
        o['numWidows'] += p['numWidows']

        utils.deepupdate(o['counters'], p['counters'])
        reCalculateValues(o['counters'])


    return output_phases
