# Copyright (c) 2017, Medicine Yeh

import os
import copy
from typing import Tuple


def reduce_linux_kernel_folder_hierarchy(file_list: list) -> list:
    ''' Reduce the target dependent folders for better prfiling.
    This helps to analyze the kernel behaviors since these folders
    are ment to be the same level.
    '''
    ret_list = copy.copy(file_list)
    for path in ret_list:
        if path.find("/linux/"):
            path = path.replace("/include/", "/")
            path = path.replace("/arch/arm/", "/arch_arm/")
            path = path.replace("/arch/arm64/", "/arch_arm64/")
            path = path.replace("/arch/x86/", "/arch_x86/")

    return ret_list


def common_prefix(path1: str, path2: str) -> Tuple[float, str]:
    ''' Find the common prefix with its distance (ratio).
    The inputs must be both absolute path or comparable relative path.
    Returns:
        tuple of (common_ratio, prefix).
    '''
    p1 = path1.split('/')
    p2 = path2.split('/')

    common_path = [kv[0] for kv in zip(p1, p2) if kv[0] == kv[1]]
    common_ratio = len(common_path) / max(len(p1), len(p2))

    return (common_ratio, '/'.join(common_path))


def locate_working_directory(file_list: list) -> list:
    ''' Try to find working directory out of a file list.
    It is better to pass in the list to all files used in
    this(target/profiled) project.
    '''
    # Retrieve dir list in 'sorted order'!!
    dir_list = sorted([os.path.split(f)[0] for f in file_list])
    if len(dir_list) == 0:
        return []

    # Add terminating empty string for handling the last element comparison
    dir_list = dir_list + ['']
    prefix_set = set()
    last_prefix = ''
    for dir_name in dir_list:
        (common_ratio, prefix) = common_prefix(last_prefix, dir_name)
        # Add common prefix to the set if it is quite different than the previous one
        if common_ratio < 0.5:
            prefix_set.add(last_prefix)
            last_prefix = dir_name
        else:
            last_prefix = prefix

    # Remove empty string from set if present
    prefix_set.discard('')
    prefix_list = list(prefix_set)

    # print('Possible working directories: {}'.format(prefix_list))
    return prefix_list


def parse_file_list(phases: list) -> set:
    ''' Parse file list out of phases. Return [] if nothing.
    This is a helper function to retrieve all the file list out
    of the process phase info.
    Exception of key not found if fail or wrong input.
    '''
    file_list = set()
    # Parse codes out of phases
    for phase in phases:
        # ':'.join()... is designed to remove string only after the last matching ':'
        file_list |= set(':'.join(code['line'].split(':')[:-1]) for code in phase['codes'])

    # Remove empty string from set if present
    file_list.discard('')
    return list(file_list)


def resolve_path(phases: list) -> None:
    ''' Resolve all tha path of codes and lines in each phase.
    This function is an inplace update function.
    This is a helper function to solve the . and .. in the path.
    No return value.
    '''
    for phase in phases:
        for code in phase['codes']:
            code['line'] = os.path.normpath(code['line'])
