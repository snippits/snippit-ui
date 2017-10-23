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
