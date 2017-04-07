#!/usr/bin/python3
import os
import sys
import getopt
import glob
import json
import collections
import copy
import re
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import textwrap

output_path = os.path.join(os.path.dirname(__file__), '..', 'public', 'output')

def write_to_file(fname, content):
    with open(fname, "w") as fp:
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
    list_json_code_list = list(json_code_list)
    lib_prefix = []
    lib_white_list = ['(.*\/target\/arm-linux-gnueabi[-\w]*\/)', # ex: /target/arm-linux-gnueabihf/
                      '(.*\/linaro-arm-linux-gnueabi[-\w]*\/)',  # ex: /linaro-arm-linux-gnueabihf/
                      '(.*\/)libstdc\+\+.\w+\d\/include\/',      # ex: libstdc++/4.9.3/include/
                      '(.*\/)libstdc\+\+.\w+\d\/src\/',          # ex: libstdc++/4.9.3/src/
                      '(.*\/)libstdc\+\+.\w+\d\/lib',            # ex: libstdc++/4.9.3/lib/
                      '(.*\/)include\/c\+\+\/[\d\.]+\/'          # ex: include/c++/4.9.3/
                      ]
    for path in list_json_code_list:
        for w in lib_white_list:
            m = re.search(w, path)
            if (m): lib_prefix.append(m.group(0))
    lib_prefix = list(set(lib_prefix))

    dir_list = []
    for path in list_json_code_list:
        c = [lp for lp in lib_prefix if path.startswith(lp)]
        if (len(c) > 0): continue
        dir_list.append(os.path.split(path)[0] + "/")
    prefix = os.path.commonprefix(dir_list)
    # print("Library prefix: {}".format(lib_prefix))
    # print("Common prefix: {}".format(prefix))

    sorted_list = collections.OrderedDict(sorted(json_code_list.items()))
    treemap = collections.OrderedDict()
    # NOTE This is needed if root node wanted to be shown
    # treemap["."] = {"id":".", "name":"./"}
    for k, v in sorted_list.items():
        # NOTE: This is too slow
        # k = "./" + os.path.relpath(k, prefix)

        # NOTE: Faster version of removing prefix.
        # P.S. /A/B/C/../../../ would be ./../../../
        k = k.replace(prefix, './')
        # Replace standard library headers and srouces into another sub-folder
        for p in lib_prefix:
            k = k.replace(p, './Standard Lib/')
        # NOTE for linux kernel only, replace the include folder
        if (prefix.find("/linux/")):
            k = k.replace("/include/", "/")
            k = k.replace("/arch/arm/", "/arch_arm/")
            k = k.replace("/arch/arm64/", "/arch_arm64/")
            k = k.replace("/arch/x86/", "/arch_x86/")
        p, l = k.split(":")
        treemap = add_node_to_treemap(treemap, p, int(v))
        # print(p, l, v)
    # print(treemap)
    # print(sorted_list)
    output_json = list(treemap.values())
    # print(output_json)
    # output_str = json.dumps(output_json, indent=4, separators=(',', ': '), sort_keys=True)
    output_str = json.dumps(output_json)
    # print(output_str)
    return output_str

def read_source_code_file(fname):
    try:
        with open(fname) as fp:
            return fp.readlines()
    except OSError:
        return ""

def append_count_to_code(code, value):
    return "{:8}{}".format(str(value), code)

def parse_codes(data):
    output_str = ""
    file_content_map = {}
    for key, value in data.items():
        fname = key.split(':')[0]
        line = int(key.split(':')[1])
        if fname in file_content_map:
            while(True):
                try:
                    file_content_map[fname][line] = append_count_to_code(file_content_map[fname][line], value)
                    break
                except IndexError:
                    # TODO Find out why and solve it properly
                    line -= 1
        else:
            try:
                if (os.path.isfile(fname)):
                    file_content_map[fname] = read_source_code_file(fname);
                    file_content_map[fname][line] = append_count_to_code(file_content_map[fname][line], value)
            except IndexError:
                pass

    for key in file_content_map:
        output_str += "==> %s <==\n" % key
        for line in file_content_map[key]:
            if ('0' <= line[0] <= '9'):
                output_str += line
            else:
                # Align the text when it has no line #
                output_str += "        " + line
    return output_str

def read_phase_timeline(path):
    with open(os.path.join(path, 'phase_history')) as fp:
        raw_order = fp.readline()
    order = list(map(int, raw_order.split(',')))

    try:
        with open(os.path.join(path, 'phase_timestamp')) as fp:
            raw_timestamp = fp.readline()
        # Parse to int and translate into miliseconds
        # x is in string type
        timestamp = [int(int(x) / 1000) for x in raw_timestamp.split(',')]
    except FileNotFoundError:
        timestamp = range(len(order))

    # Find maximum phase id
    maximum_phase_id = max(order)
    # Rephrase the value of special number
    for i in range(len(order)):
        if (order[i] == -1): # Means a null point
             order[i] = None
    # Zip two list together and output in this form [[int, int], ...]
    phases = zip(timestamp, order)
    phases = [ [kv[0],kv[1]] for kv in phases ]
    return phases, maximum_phase_id


def legacy_get_execution_time(prof_message_str):
    hit_flag = False# DCE
    return (float(prof_message_str.split(":")[-1].split(" ")[1]))

def parse_prof_text(prof_string):
    prof_string = prof_string.replace(",", "")
    prof_string = prof_string.replace("(", "")
    prof_string = prof_string.replace(")", "")
    prof_string = prof_string.replace("|", "")
    output = []
    for line in prof_string.split():
        try:
            # either nan or -nan should be escaped
            if (line.lower() == "nan" or line.lower() == "-nan"):
                output.append(0.0)
                continue
            output.append(float(line))
        except ValueError:
            pass
    # TODO VPMU output miss L2-D when it's all zeros
    if (len(output) != 40):
        output = [*output[:30], 0.0, 0, 0, 0, *output[30:]]
    return output

def parse_phase_files(path, output_path, parse_code_flag, walk_times_filter):
    files = glob.glob(os.path.join(path, 'phase-*'))

    code_files_array = []
    exe_time_array = []
    perf_cnt_array = []
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
        perf_cnt_array.append(parse_prof_text(prof_message["text"]))
        prof_message_str = json.dumps(prof_message)
        exe_time = legacy_get_execution_time(prof_message_str)
        exe_time_array.append(exe_time)
        # Parse code-map to code or just output the json array after sorting by key/value
        if (parse_code_flag):
            code_str = parse_codes(json_code_list)
        else:
            # code_str = sort_by_value_str(json_code_list)
            code_str = sort_by_key_str(json_code_list)
        # Paese the code-map to a tree-map format
        treemap_str = parse_treemap(json_code_list)

        # Append to the files array and filter out files with only a few times of execution
        code_files_array.append(dict((k, v) for k, v in json_code_list.items() if v >= walk_times_filter))
        # Output all the corresponding files generated by this phase
        out_fname = os.path.join(output_path, 'phase-prof-' + str(number))
        write_to_file(out_fname, prof_message_str)
        out_fname = os.path.join(output_path, 'phase-code-' + str(number))
        write_to_file(out_fname, code_str)
        out_fname = os.path.join(output_path, 'phase-treemap-' + str(number))
        write_to_file(out_fname, treemap_str)

    out_fname = os.path.join(output_path, 'phase-exec-time-histogram')
    write_to_file(out_fname, json.dumps(sorted(exe_time_array)))
    return code_files_array, perf_cnt_array, exe_time_array

def compare_two_code_similarity(code_ahead, code_follow):
    cnt_total = len(code_ahead) + len(code_follow)
    if (cnt_total == 0): return 0.0
    # Both are unique list, so this would work
    cnt_same = len(set(code_ahead) & set(code_follow))
    return cnt_same * 2 / float(cnt_total)

def collect_phase_code_range(path, max_phase_id, code_files_array, fine_grained_flag):
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

    if (fine_grained_flag):
        sim_vec = [0.91,  0.92,  0.93,  0.94,  0.95,  0.96,  0.97,  0.98,  0.99, 1.0]
    else:
        sim_vec = [0.1,  0.2,  0.3,  0.4,  0.5,  0.6,  0.7,  0.8,  0.9, 1.0]
    for idx, threshold in enumerate(sim_vec):
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
        if (kv[1] is not None):
            kv[1] = code_refer_array[kv[1]]
    return pl

def reduce_phase_timeline(phase_list):
    last_id = -1
    last_time = -1
    output_list = []
    for p in phase_list:
        if (p[1] != last_id or p[0] - last_time > 100):
            output_list.append(p)
            last_time = p[0]
        last_id = p[1]
    return output_list

def filter_phase_timeline(phase_list, exe_time_array, value):
    output_list = []
    for p in phase_list:
        if (exe_time_array[p[1]] >= value):
            output_list.append(p)
        else:
            output_list.append([p[0], None])
    return output_list

def output_phase_timeline(path, idx, phase_list):
    with open(os.path.join(path, 'phase-history-' + str(idx) + '.json'), "w") as out_file:
        json.dump(phase_list, out_file)
    # TODO make it shorter
    out_str = ""
    # shown_range = range(2800, 3700)
    shown_range = range(len(phase_list))
    for i in shown_range:
        out_str += str(i) + ","
    out_str += "\n"
    cnt = 0
    for kv in phase_list:
        if (cnt >= shown_range[0] and cnt <= shown_range[-1]):
            out_str += str(kv[1]) + ","
        cnt += 1
    out_str += "\n"
    write_to_file(os.path.join(path, 'phase-history-' + str(idx) + '.csv'), out_str)

def output_phase_files(path, output_path, prof_cnt_array, code_list_array, parse_code_flag):
    files = glob.glob(os.path.join(path, 'phase-*'))

    for f in sorted(files):
        number = int(f.split('-')[1])
        prof_cnt = prof_cnt_array[number]
        # Get the profiling information
        text_prof = \
"""==== Program Profile ====

   === QEMU/ARM ===
Instructions:
 Total instruction count       : {:,d}
  ->User mode insn count       : {:,d}
  ->Supervisor mode insn count : {:,d}
  ->IRQ mode insn count        : {:,d}
  ->Other mode insn count      : {:,d}
 Total load instruction count  : {:,d}
  ->User mode load count       : {:,d}
  ->Supervisor mode load count : {:,d}
  ->IRQ mode load count        : {:,d}
  ->Other mode load count      : {:,d}
 Total store instruction count : {:,d}
  ->User mode store count      : {:,d}
  ->Supervisor mode store count: {:,d}
  ->IRQ mode store count       : {:,d}
  ->Other mode store count     : {:,d}
Branch:
    -> predict accuracy    : ({:.2f})
    -> correct prediction  : ({:,d})
    -> wrong prediction    : ({:,d})
CACHE:
       (Miss Rate)   |    Access Count    |   Read Miss Count  |  Write Miss Count  |
    -> memory ({:.3f}) |{:=20,d}|{:=20,d}|{:=20,d}|
    -> L1-I   ({:.3f}) |{:=20,d}|{:=20,d}|{:=20,d}|
    -> L1-D   ({:.3f}) |{:=20,d}|{:=20,d}|{:=20,d}|
    -> L2-D   ({:.3f}) |{:=20,d}|{:=20,d}|{:=20,d}|

Timing Info:
  ->CPU                        : {:f} sec
  ->Branch                     : {:f} sec
  ->Cache                      : {:f} sec
  ->System memory              : {:f} sec
  ->I/O memory                 : {:f} sec
Estimated execution time       : {:f} sec
""".format(*prof_cnt)

        prof_message = {"text": text_prof}
        prof_message_str = json.dumps(prof_message)
        json_code_list = code_list_array[number]
        if (parse_code_flag):
            code_str = parse_codes(json_code_list)
        else:
            # code_str = sort_by_value_str(json_code_list)
            code_str = sort_by_key_str(json_code_list)

        # Paese the code-map to a tree-map format
        treemap_str = parse_treemap(code_list_array[number])

        out_fname = os.path.join(output_path, 'phase-prof-' + str(number))
        write_to_file(out_fname, prof_message_str)
        out_fname = os.path.join(output_path, 'phase-code-' + str(number))
        write_to_file(out_fname, code_str)
        out_fname = os.path.join(output_path, 'phase-treemap-' + str(number))
        write_to_file(out_fname, treemap_str)

def merge_phases(perf_cnt_array, code_list_array, code_refer_array, selected_similarity):
    # Accumulate the counters of phases
    for i in range(len(perf_cnt_array)):
        for j in range(len(perf_cnt_array[i])):
            if (j not in [15, 18, 22, 26, 30, 34, 35, 36, 37, 38, 39]):
                perf_cnt_array[i][j] = int(perf_cnt_array[i][j])

    for i in range(len(perf_cnt_array)):
        # TODO Unknown bug. Why doesn't it match?
        if (i == len(code_refer_array[selected_similarity - 1])): break
        to_num = code_refer_array[selected_similarity - 1][i]
        if (to_num == i): continue;
        for k in code_list_array[i].keys():
            try:
                code_list_array[to_num][k] += code_list_array[i][k]
            except KeyError:
                code_list_array[to_num][k] = code_list_array[i][k]
        _tmp = [x + y for x, y in zip(perf_cnt_array[to_num], perf_cnt_array[i])]
        perf_cnt_array[to_num] = _tmp
        # TODO Divide by zero problem
        perf_cnt_array[to_num][15] = perf_cnt_array[to_num][16] / (perf_cnt_array[to_num][16] + perf_cnt_array[to_num][17] + 1)
        perf_cnt_array[to_num][18] = 0.0
        perf_cnt_array[to_num][22] = (perf_cnt_array[to_num][24] + perf_cnt_array[to_num][26]) / (perf_cnt_array[to_num][23] + 1)
        perf_cnt_array[to_num][26] = (perf_cnt_array[to_num][28] + perf_cnt_array[to_num][29]) / (perf_cnt_array[to_num][27] + 1)
        perf_cnt_array[to_num][30] = (perf_cnt_array[to_num][32] + perf_cnt_array[to_num][33]) / (perf_cnt_array[to_num][31] + 1)

def get_descriptions():
    return textwrap.dedent('''\
    A parser for snippits UI web interface.
    ''')

def get_sample_usage():
    return textwrap.dedent('''\
    Sample Usage:
            Ex: parse.py -i /tmp/snippit/phase/740
        Parse code lines into texts
            Ex: parse.py -i /tmp/snippit/phase/740 -c
        Only Timeline changes
            Ex: parse.py -i /tmp/snippit/phase/740 -f
        Merge the results with teh same similarity index 9
            Ex: parse.py -i /tmp/snippit/phase/740 -f -m 9
    ''')

def main(argv):
    global output_path

    ap = ArgumentParser('parse.py',
            formatter_class=RawDescriptionHelpFormatter,
            description=get_descriptions(),
            epilog=get_sample_usage())
    ap.add_argument('--input', '-i', help='Input Directory', type=str)
    ap.add_argument('--output', '-o', help='Output Directory', type=str, default=output_path)
    ap.add_argument('--code_parser', '-c', help='Parse the codes', action='store_true')
    ap.add_argument('--fine_grained', '-f', help='Use similarity 0.9-0.99', action='store_true')
    ap.add_argument('--time_filter', '-t', help='Filter out phases shorter than # secs', type=float)
    ap.add_argument('--merge_similarity', '-m', help='# of index of similarity to be merged', type=int)
    ap.add_argument('--walk_times_filter', '-w',
            help='Filter out lines which contains less than # times. Default=10', type=int, default=10)
    args = ap.parse_args()

    input_path = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)

    print('Input path is  : ' + input_path)
    print('Output file is : ' + output_path)

    if (not os.path.isdir(input_path)):
        print("Input path is not a directory")
        sys.exit(2)
    if (not os.path.isdir(output_path)):
        print("Output path is not a directory")
        sys.exit(2)

    phase_timeline,num_phases = read_phase_timeline(input_path)
    print('# Phases: {}'.format(num_phases))
    print('# Windows: {}'.format(len(phase_timeline)))

    phase_code_range, perf_cnt_array, exe_time_array = parse_phase_files(input_path, output_path, args.code_parser, args.walk_times_filter)
    print('\nParse Finished')

    print('Calculating similarity of phases... (It might take some time)')
    code_refer_array = collect_phase_code_range(input_path, num_phases, phase_code_range, args.fine_grained)
    # print('Remap phase IDs as follows:')
    # print(code_refer_array)
    out_fname = os.path.join(output_path, 'phase-similarity')
    write_to_file(out_fname, json.dumps(code_refer_array))
    if (args.merge_similarity):
        print('Selected similarity is {}'.format(args.merge_similarity))
        merge_phases(perf_cnt_array, phase_code_range, code_refer_array, args.merge_similarity)
        # Output the counters
        output_phase_files(input_path, output_path, perf_cnt_array, phase_code_range, args.code_parser)

    reduced_len = 0
    for idx in range(len(code_refer_array)):
        pl = update_phase_id(phase_timeline, code_refer_array[idx])
        # Reduce timeline if # windows exceeds 10,000
        # NOTE This would be replaced by scaling in the future
        if (len(pl) > 10000):
            pl = reduce_phase_timeline(pl)
        # Watch only the phase longer than # of seconds
        if (args.time_filter):
            pl = filter_phase_timeline(pl, exe_time_array, args.time_filter)
        reduced_len = len(pl)
        output_phase_timeline(output_path, idx + 1, pl)
    print('Output timeline with # windows: {}'.format(reduced_len))

if __name__ == "__main__":
    main(sys.argv[1:])

