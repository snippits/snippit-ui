# Copyright (c) 2017, Medicine Yeh
import copy

import myutils.createMappingTable as createMappingTable

cached_mappingTable = {}
cached_simTh = 0
cached_simMat = {}
def getPhaseMappingTable(simMat, simTh):
    global cached_mappingTable, cached_simTh
    if (simMat is cached_simMat and simTh == cached_simTh):
        return cached_mappingTable

    cached_mappingTable = createMappingTable.nearestAbove(simMat, simTh)

    return cached_mappingTable

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

        b = o['counters']['branch']
        b['hit'] += p['counters']['branch']['hit']
        b['miss'] += p['counters']['branch']['miss']
        b['accuracy'] = b['hit'] / (b['hit'] + b['miss'])

        c = o['counters']['cache']['dCache']
        c['accessCount'] += p['counters']['cache']['dCache']['accessCount']
        c['readMiss'] += p['counters']['cache']['dCache']['readMiss']
        c['writeMiss'] += p['counters']['cache']['dCache']['writeMiss']
        c['missRate'] = (c['readMiss'] + c['writeMiss']) / c['accessCount']
        c = o['counters']['cache']['iCache']
        c['accessCount'] += p['counters']['cache']['iCache']['accessCount']
        c['readMiss'] += p['counters']['cache']['iCache']['readMiss']
        c['writeMiss'] += p['counters']['cache']['iCache']['writeMiss']
        c['missRate'] = (c['readMiss'] + c['writeMiss']) / c['accessCount']
        c = o['counters']['cache']['level2']
        if (c):
            c['accessCount'] += p['counters']['cache']['level2']['accessCount']
            c['readMiss'] += p['counters']['cache']['level2']['readMiss']
            c['writeMiss'] += p['counters']['cache']['level2']['writeMiss']
            c['missRate'] = (c['readMiss'] + c['writeMiss']) / c['accessCount']

        o['counters']['instruction']['cycle'] += p['counters']['instruction']['cycle']
        o['counters']['instruction']['system'] += p['counters']['instruction']['system']
        o['counters']['instruction']['total'] += p['counters']['instruction']['total']
        o['counters']['instruction']['user'] += p['counters']['instruction']['user']

        o['counters']['load']['system'] += p['counters']['load']['system']
        o['counters']['load']['total'] += p['counters']['load']['total']
        o['counters']['load']['user'] += p['counters']['load']['user']

        o['counters']['store']['system'] += p['counters']['store']['system']
        o['counters']['store']['total'] += p['counters']['store']['total']
        o['counters']['store']['user'] += p['counters']['store']['user']

        o['counters']['time']['branch'] += p['counters']['time']['branch']
        o['counters']['time']['cache'] += p['counters']['time']['cache']
        o['counters']['time']['cpu'] += p['counters']['time']['cpu']
        o['counters']['time']['host'] += p['counters']['time']['host']
        o['counters']['time']['ioMemory'] += p['counters']['time']['ioMemory']
        o['counters']['time']['systemMemory'] += p['counters']['time']['systemMemory']
        o['counters']['time']['target'] += p['counters']['time']['target']

    return output_phases
