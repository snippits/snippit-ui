# Copyright (c) 2017, Medicine Yeh

from functools import lru_cache

from myutils.utils import Hashable


class Event:
    CONTEXT_SWITCH = 1


@lru_cache(maxsize=32)
def remap(phase_timeline, mapping_table):
    ret = [[kv[0], mapping_table[kv[1]]] for kv in phase_timeline]
    return Hashable(ret)


@lru_cache(maxsize=32)
def append_event(phase_timeline, event_list, event):
    ret = [[kv[0], None] for kv in event_list if kv[1] == event]
    return Hashable(phase_timeline + ret)


def append_events_in_order(phase_timeline, event_list, events):
    time_list = [kv for kv in event_list if kv[1] in events]
    # Merge two timeline in sorted order
    ret = sorted(phase_timeline + time_list)
    return ret
