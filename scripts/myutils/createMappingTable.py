import numpy as np

def npNearestAbove(simMat, simTh = 1.0):
    num_phases = len(simMat)
    # Restrict the range to (0, 1)
    simTh = min(max(simTh, 0.000001), 0.999999)

    # Get lower triangle with diagonal
    m = np.tril(simMat)
    # Find the nearest value above the threshold
    mapping = np.ma.masked_array(m, mask = m < float(simTh)).argmin(axis=1)

    # Create identical mapping first
    table = list(range(num_phases))
    for i,m in enumerate(mapping):
        table[i] = table[m]
    return table

def npEarliestMatch(simMat, simTh = 1.0):
    num_phases = len(simMat)
    # Restrict the range to (0, 1)
    simTh = min(max(simTh, 0.000001), 0.999999)

    # Find the first match above the threshold
    mapping = np.argmax(np.array(simMat) >= float(simTh), axis=1)

    # Create identical mapping first
    table = list(range(num_phases))
    for i,m in enumerate(mapping):
        table[i] = table[m]
    return table

def earliestMatch(simMat, simTh = 1.0):
    num_phases = len(simMat)
    # Restrict the range to (0, 1)
    simTh = min(max(simTh, 0.000001), 0.999999)

    # Create identical mapping first
    mappingTable = list(range(num_phases))
    for i in range(len(mappingTable)):
        for j in range(0, i):
            if (simMat[i][j] >= simTh):
                #print(str(mappingTable[i]) + 'to' + str(mappingTable[j]))
                mappingTable[i] = mappingTable[j]
                break
    return mappingTable
