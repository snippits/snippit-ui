# Copyright (c) 2017, Medicine Yeh

from functools import lru_cache


class EVENT:
    CONTEXT_SWITCH = 1


@lru_cache(maxsize=32)
def remap(phase_timeline, mapping_table):
    ret = [[kv[0], mapping_table[kv[1]]] for kv in phase_timeline]
    return ret


@lru_cache(maxsize=32)
def get_event_time_list(event_timeline, event=EVENT.CONTEXT_SWITCH):
    ret = [[kv[0], None] for kv in event_timeline if kv[1] == event]
    return ret
