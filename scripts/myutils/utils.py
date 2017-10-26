# Copyright (c) 2017, Medicine Yeh

from myutils import mapping_table


def get_phase_mapping(sim_mat, sim_thold=1.0):
    return mapping_table.nearest_above(sim_mat, sim_thold)


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
