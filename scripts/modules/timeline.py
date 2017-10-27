# Copyright (c) 2017, Medicine Yeh

from functools import lru_cache

from myutils.utils import Hashable


class Event:
    CONTEXT_SWITCH = 1


def apply_mapping(mapping_table: list, index: int = None) -> int:
    '''Apply list index with None type acceptable
    List does not take None type as its index, this function help to return
    None when the index is None
    '''
    if index is not None:
        return mapping_table[index]
    return None


@lru_cache(maxsize=32)
def remap(phase_timeline: list, mapping_table: list) -> list:
    '''Remap the timeline with a mapping table.
    The mapping table is a ID table where its index means its ID and
    its value means its target ID.
    '''
    ret = [[kv[0], apply_mapping(mapping_table, kv[1])] for kv in phase_timeline]
    return Hashable(ret)


@lru_cache(maxsize=32)
def append_event(phase_timeline: list, event_list: list, event: int) -> list:
    ret = [[kv[0], None] for kv in event_list if kv[1] == event]
    return Hashable(phase_timeline + ret)


def append_events_in_order(phase_timeline: list, event_list: list, events: list) -> list:
    time_list = [kv for kv in event_list if kv[1] in events]
    # Merge two timeline in sorted order
    ret = sorted(phase_timeline + time_list)
    return ret
