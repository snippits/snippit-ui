#!/bin/python
import os
import sys
import getopt
import glob
import json
import linecache

output_dir = os.path.join(os.path.dirname(sys.argv[0]), '..', 'public', 'output')

def read_phase_history(path):
    fp = open(os.path.join(path, 'phase_history'))
    raw_order = fp.readline()
    order = raw_order.split(',')
    phases = map(int, order)
    return list(phases)

def output_phase_history_json(path, phase_list):
    fp = open(os.path.join(path, 'phase_history.json'), "w")
    last_idx = len(phase_list) - 1
    fp.write("[")
    for idx, val in enumerate(phase_list):
        out_str = "[" + str(idx) + "," + str(val) + "]"
        fp.write(out_str)
        if (idx != last_idx):
            fp.write(",")
    fp.write("]\n")

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

    return {'code': json.loads(json_code_list), 'prof': prof_string}

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
            if (os.path.isfile(fname)):
                file_content_map[fname] = read_source_code_file(fname);
                file_content_map[fname][line] = append_count_to_code(file_content_map[fname][line], value)

    for key in file_content_map:
        output_str += "==> " + key + " <==\n"
        for line in file_content_map[key]:
            if (line[0] >= '0' and line[0] <= '9'):
                output_str += line
            else:
                # Align the text when it has no line #
                output_str += "        " + line
    return output_str

def write_to_file(fname, content):
    fp = open(fname, "w")
    fp.write(content)

def parse_phase_files(path, output_path):
    files = glob.glob(os.path.join(path, 'phase-*'))

    for f in files:
        print('Parsing ' + f)
        number = int(f.split('-')[1])
        ret = read_single_phase_file(f)
        json_code_list = ret['code']
        prof_message = ret['prof']
        output_str = parse_codes(json_code_list)

        out_fname = os.path.join(output_path, 'phase-prof-' + str(number))
        write_to_file(out_fname, prof_message)
        out_fname = os.path.join(output_path, 'phase-code-' + str(number))
        write_to_file(out_fname, output_str)

def print_usage():
    print('Usage: parse.py -i <PHASE DIRECTORY>/<PID>')
    print('    Ex: parse.py -i /tmp/snippit/phase/740')

def main(argv):
    global output_dir
    input_path = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:")
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
           output_dir = arg
    if (os.path.isdir(input_path)):
        print('Input path is  ' + input_path)
        print('Output file is ' + output_dir)
        phase_list = read_phase_history(input_path)
        output_phase_history_json(output_dir, phase_list)
        print('# Windows: {}'.format(len(phase_list)))
        parse_phase_files(input_path, output_dir)
    else:
        print("Input path is not a directory")
        sys.exit(2)

if __name__ == "__main__":
    main(sys.argv[1:])

