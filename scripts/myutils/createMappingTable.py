try:
    import numpy as np
    USE_NP = True
except ImportError:
    USE_NP = False

def buildMappingTable(mapping):
    # Create identical mapping first
    table = list(range(len(mapping)))
    # Update new reference in-place
    for i,m in enumerate(mapping):
        table[i] = table[m]
    return table

def npNearestAbove(simMat, simTh = 1.0):
    num_phases = len(simMat)
    # Restrict the range to (0, 1)
    if (simTh == 1.0): return list(range(len(simMat)))
    if (simTh == 0.0): return [0] * len(simMat)

    # Get lower triangle with diagonal
    m = np.tril(simMat)
    # Find the nearest value above the threshold
    mapping = np.ma.masked_array(m, mask = m < float(simTh)).argmin(axis=1)

    return buildMappingTable(mapping)

def npEarliestMatch(simMat, simTh = 1.0):
    num_phases = len(simMat)
    # Restrict the range to (0, 1)
    if (simTh == 1.0): return list(range(len(simMat)))
    if (simTh == 0.0): return [0] * len(simMat)

    # Find the first match above the threshold
    mapping = np.argmax(np.array(simMat) >= float(simTh), axis=1)

    return buildMappingTable(mapping)

def nearestAbove(simMat, simTh = 1.0):
    num_phases = len(simMat)
    # Restrict the range to (0, 1)
    if (simTh == 1.0): return list(range(len(simMat)))
    if (simTh == 0.0): return [0] * len(simMat)

    # Create identical mapping first
    mappingTable = list(range(num_phases))
    for i in range(len(mappingTable)):
        matched_v = 0
        matched_i = 0
        for j in range(0, i):
            if (simMat[i][j] >= simTh and matched_v <= simMat[i][j]):
                matched_i = j
                matched_v = simMat[i][j]
                break
        mappingTable[i] = mappingTable[matched_i]
    return mappingTable

def earliestMatch(simMat, simTh = 1.0):
    num_phases = len(simMat)
    # Restrict the range to (0, 1)
    if (simTh == 1.0): return list(range(len(simMat)))
    if (simTh == 0.0): return [0] * len(simMat)

    # Create identical mapping first
    mappingTable = list(range(num_phases))
    for i in range(len(mappingTable)):
        for j in range(0, i):
            if (simMat[i][j] >= simTh):
                mappingTable[i] = mappingTable[j]
                break
    return mappingTable

if USE_NP:
    earliestMatch = npEarliestMatch
    nearestAbove = npNearestAbove
else:
    earliestMatch = earliestMatch
    nearestAbove = nearestAbove
