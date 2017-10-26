# Copyright (c) 2017, Medicine Yeh

try:
    import numpy as np
    USE_NP = True
except ImportError:
    USE_NP = False


def remap(table, mapping):
    # Update new reference in-place
    for i, m in enumerate(mapping):
        table[i] = table[m]
    return table


def np_nearest_above(sim_mat, sim_thold=1.0):
    num_phases = len(sim_mat)
    # Restrict the range to (0, 1)
    if (sim_thold == 1.0): return list(range(len(sim_mat)))
    if (sim_thold == 0.0): return [0] * len(sim_mat)

    # Get lower triangle with diagonal
    m = np.tril(sim_mat)
    # Find the nearest value above the threshold
    mapping = np.ma.masked_array(m, mask=m < float(sim_thold)).argmin(axis=1)

    # Create identical mapping first
    table = list(range(len(mapping)))
    return remap(table, mapping)


def np_earliest_match(sim_mat, sim_thold=1.0):
    num_phases = len(sim_mat)
    # Restrict the range to (0, 1)
    if (sim_thold == 1.0): return list(range(len(sim_mat)))
    if (sim_thold == 0.0): return [0] * len(sim_mat)

    # Find the first match above the threshold
    mapping = np.argmax(np.array(sim_mat) >= float(sim_thold), axis=1)

    # Create identical mapping first
    table = list(range(len(mapping)))
    return remap(table, mapping)


def nearest_above(sim_mat, sim_thold=1.0):
    num_phases = len(sim_mat)
    # Restrict the range to (0, 1)
    if (sim_thold == 1.0): return list(range(len(sim_mat)))
    if (sim_thold == 0.0): return [0] * len(sim_mat)

    # Create identical mapping first
    mappingTable = list(range(num_phases))
    for i in range(len(mappingTable)):
        matched_v = 0
        matched_i = 0
        for j in range(0, i):
            if (sim_mat[i][j] >= sim_thold and matched_v <= sim_mat[i][j]):
                matched_i = j
                matched_v = sim_mat[i][j]
                break
        mappingTable[i] = mappingTable[matched_i]
    return mappingTable


def earliest_match(sim_mat, sim_thold=1.0):
    num_phases = len(sim_mat)
    # Restrict the range to (0, 1)
    if (sim_thold == 1.0): return list(range(len(sim_mat)))
    if (sim_thold == 0.0): return [0] * len(sim_mat)

    # Create identical mapping first
    mappingTable = list(range(num_phases))
    for i in range(len(mappingTable)):
        for j in range(0, i):
            if (sim_mat[i][j] >= sim_thold):
                mappingTable[i] = mappingTable[j]
                break
    return mappingTable


if USE_NP:
    earliest_match = np_earliest_match
    nearest_above = np_nearest_above
