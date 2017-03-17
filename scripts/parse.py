#!/usr/bin/python3
from __future__ import unicode_literals, print_function
import os
import sys
import getopt
import glob
import json
import collections
import copy

output_path = os.path.join(os.path.dirname(__file__), '..', 'public', 'output')

def write_to_file(fname, content):
    fp = open(fname, "w")
    fp.write(content)

def sort_by_value_str(json_code_list):
    json_code_list = sorted(json_code_list.items(), key=lambda kv: -kv[1])
    output_str = '[\n'
    for kv in json_code_list[:-1]:
        output_str += '{"%s": %d},\n' % kv
    output_str += '{"%s": %d}\n]' % json_code_list[-1]
    return output_str

def sort_by_key_str(json_code_list):
    return json.dumps(json_code_list, indent=4, separators=(',', ': '), sort_keys=True)

def read_single_phase_file(fname):
    fp = open(fname)
    json_code_list = ""
    prof_string = ""
    json_flag = False
    prof_flag = False
    content = fp.readlines()
    for line in content:
        if (line == '{\n'): json_flag = True
        if (json_flag): json_code_list += line
        if (line == '}\n'): json_flag = False
        if (line == '==== Program Profile ====\n'): prof_flag = True
        if (prof_flag): prof_string += line

    prof_ret = {"text": prof_string}
    if (json_code_list == ""):
        json_code_list = "{}"
    return {'code': json.loads(json_code_list), 'prof': prof_ret}

def add_node_to_treemap(treemap, relative_path, counter):
    dirs = relative_path.split("/")
    # filename with path
    for i in range(1, len(dirs)):
        _parent = os.path.join(*dirs[:i])
        _id = _parent + "/" + dirs[i]
        # NOTE Remove this if root node wanted to be shown
        if (_parent == "."): _parent = None
        if (_id in treemap):
            treemap[_id]["value"] += counter
        else:
            treemap[_id] = {
                    "id": _id,
                    "parent": _parent,
                    "name": dirs[i],
                    "value": counter,
                    # "color": "#FF0000",
                };
        # print(_parent, dirs[i])

    return treemap

def parse_treemap(json_code_list):
    # id_map = get_unique_id_mapping(json_code_list)
    prefix = os.path.commonprefix(list(json_code_list))
    sorted_list = collections.OrderedDict(sorted(json_code_list.items()))
    treemap = collections.OrderedDict()
    # NOTE This is needed if root node wanted to be shown
    # treemap["."] = {"id":".", "name":"./"}
    for k, v in sorted_list.items():
        # NOTE: This is too slow
        # k = "./" + os.path.relpath(k, prefix)

        # NOTE: Faster version of removing prefix.
        # P.S. /A/B/C/../../../ would be ../../../
        k = k[len(prefix):]
        # Check if it is in "./" format
        if (k[0] != "."): k = "./" + k

        # NOTE for linux kernel only, replace the include folder
        k = k.replace("/include/", "/")
        k = k.replace("/arch/arm/", "/arch_arm/")
        k = k.replace("/arch/arm64/", "/arch_arm64/")
        k = k.replace("/arch/x86/", "/arch_x86/")
        p, l = k.split(":")
        treemap = add_node_to_treemap(treemap, p, int(v))
        # print f, l, v
    # print(treemap)
    # print(sorted_list)
    output_json = list(treemap.values())
    # print(output_json)
    # output_str = json.dumps(output_json, indent=4, separators=(',', ': '), sort_keys=True)
    output_str = json.dumps(output_json)
    # print(output_str)
    return output_str

def read_source_code_file(fname):
    if (os.path.isfile(fname)):
        fp = open(fname)
        content = fp.readlines()
        fp.close()
        return content
    return ""

def append_count_to_code(code, value):
    return "{:8}{}".format(str(value), code)

def parse_codes(data):
    output_str=""
    file_content_map = {}
    for key, value in data.items():
        fname=key.split(':')[0]
        line=int(key.split(':')[1])
        if fname in file_content_map:
            file_content_map[fname][line] = append_count_to_code(file_content_map[fname][line], value)
        else:
            try:
                if (os.path.isfile(fname)):
                    file_content_map[fname] = read_source_code_file(fname);
                    file_content_map[fname][line] = append_count_to_code(file_content_map[fname][line], value)
            except IndexError:
                pass

    for key in file_content_map:
        output_str += "==> " + key + " <==\n"
        for line in file_content_map[key]:
            if (line[0] >= '0' and line[0] <= '9'):
                output_str += line
            else:
                # Align the text when it has no line #
                output_str += "        " + line
    return output_str

def read_phase_timeline(path):
    fp = open(os.path.join(path, 'phase_history'))
    raw_order = fp.readline()
    order = list(map(int, raw_order.split(',')))

    try:
        fp = open(os.path.join(path, 'phase_timestamp'))
        raw_timestamp = fp.readline()
        # Parse to int and translate into miliseconds
        timestamp = [(int(x) / 1000) for x in raw_timestamp.split(',')]
    except FileNotFoundError:
        timestamp = range(len(order))

    maximum_phase_id = max(order)
    # Zip two list together and output in this form [[int, int], ...]
    phases = zip(timestamp, order)
    phases = [ [kv[0],kv[1]] for kv in phases ]
    return phases, maximum_phase_id

def parse_phase_files(path, output_path, parse_code_flag):
    files = glob.glob(os.path.join(path, 'phase-*'))

    code_files_array = []
    for f in sorted(files):
        print('Parsing ' + f + '/' + str(len(files) - 1), end='\r')
        sys.stdout.flush()
        number = int(f.split('-')[1])
        # Read the file as whole, then parse and return objects of information we need
        ret = read_single_phase_file(f)
        # Get code-map in format {"FILE_PATH:LINE_NUM" : EXECUTED_TIMES}
        json_code_list = ret['code']
        # Get the profiling information
        prof_message = ret['prof']
        prof_message_str = json.dumps(prof_message)
        # Parse code-map to code or just output the json array after sorting by key/value
        if (parse_code_flag):
            code_str = parse_codes(json_code_list)
        else:
            code_str = sort_by_value_str(json_code_list)
            # code_str = sort_by_key_str(json_code_list)
        # Paese the code-map to a tree-map format
        treemap_str = parse_treemap(json_code_list)

        # Append to the files array and filter out files with only a few times of execution
        code_files_array.append(dict((k, v) for k, v in json_code_list.items() if v >= 10))
        # Output all the corresponding files generated by this phase
        out_fname = os.path.join(output_path, 'phase-prof-' + str(number))
        write_to_file(out_fname, prof_message_str)
        out_fname = os.path.join(output_path, 'phase-code-' + str(number))
        write_to_file(out_fname, code_str)
        out_fname = os.path.join(output_path, 'phase-treemap-' + str(number))
        write_to_file(out_fname, treemap_str)
    return code_files_array

def compare_two_code_similarity(code_ahead, code_follow):
    cnt_total = len(code_follow)
    cnt_same = 0
    for key in code_follow:
        if key in code_ahead:
            cnt_same += 1
    return cnt_same / float(cnt_total)

def collect_phase_code_range(path, max_phase_id, code_files_array):
    code_refer_array = []
    for i in range(10):
        code_refer_array.append(list(range(max_phase_id + 1)))

    # Calculate similarity matrix (upper triangle only, with transpose)
    similarity_mat = [0] * (max_phase_id + 1)
    for i in range(max_phase_id + 1):
        similarity_mat[i] = [0] * (max_phase_id + 1)
        for j in range(1, i):
            # NOTE: The order is important
            similarity = compare_two_code_similarity(code_files_array[j], code_files_array[i])
            similarity_mat[i][j] = similarity

    for kv in zip(range(10), [0.1,  0.2,  0.3,  0.4,  0.5,  0.6,  0.7,  0.8,  0.9, 1.0]):
        threshold = kv[1]
        idx = kv[0]
        for i in range(max_phase_id + 1):
            for j in range(1, i):
                # Find first hit
                if (similarity_mat[i][j] > threshold):
                    code_refer_array[idx][i] = code_refer_array[idx][j]
                    break

    return code_refer_array

def update_phase_id(phase_list, code_refer_array):
    pl = copy.deepcopy(phase_list)
    for kv in pl:
        kv[1] = code_refer_array[kv[1]]
    return pl

def output_phase_timeline(path, idx, phase_list):
    with open(os.path.join(path, 'phase-history-' + str(idx) + '.json'), "w") as out_file:
        json.dump(phase_list, out_file)

def print_usage():
    print('Usage: parse.py -i <PHASE DIRECTORY>/<PID> [-o <OUTPUT DIRECTORY>] [-c]')
    print('    Ex: parse.py -i /tmp/snippit/phase/740')
    print('\nOptions:')
    print('    -i:      Input Directory')
    print('    -o:      Output Directory')
    print('    -c:      Parse source codes and output with line# in plain text files')

def main(argv):
    global output_path
    input_path = ''
    parse_code_flag = False

    try:
        opts, args = getopt.getopt(argv,"hi:oc:")
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
       if opt == '-h':
           print_usage()
           sys.exit()
       elif opt in ("-i"):
           input_path = arg
       elif opt in ("-o"):
           output_path = arg
       elif opt in ("-c"):
           parse_code_flag = True

    if (len(opts) == 0):
        print_usage()
        sys.exit(0)

    if (os.path.isdir(input_path)):
        print('Input path is  ' + input_path)
        print('Output file is ' + output_path)

        phase_timeline,num_phases = read_phase_timeline(input_path)
        print('# Phases: {}'.format(num_phases))
        print('# Windows: {}'.format(len(phase_timeline)))

        phase_code_range = parse_phase_files(input_path, output_path, parse_code_flag)
        print('\nParse Finished')

        print('Calculating similarity of phases... (It might take some time)')
        code_refer_array = collect_phase_code_range(input_path, num_phases, phase_code_range)
        # print('Remap phase IDs as follows:')
        # print(code_refer_array)
        print('Output timeline')
        for idx in range(len(code_refer_array)):
            pl = update_phase_id(phase_timeline, code_refer_array[idx])
            output_phase_timeline(output_path, idx + 1, pl)
    else:
        print("Input path is not a directory")
        sys.exit(2)

if __name__ == "__main__":
    main(sys.argv[1:])

