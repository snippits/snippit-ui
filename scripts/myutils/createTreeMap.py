# Copyright (c) 2017, Medicine Yeh
import anytree

from collections import defaultdict
from anytree import Node, Resolver, RenderTree

treemap_unique_id = 0

# Return a unique ID
def next_id():
    global treemap_unique_id
    treemap_unique_id += 1
    return treemap_unique_id

# Transform
# From : /home/medicineyeh/Projects/qemu_arm_image/./matrix_mul.c:36
# To   : ('/home/medicineyeh/Projects/qemu_arm_image/', 'matrix_mul.c')
# From : ld-linux.so.3
# To   : ('None', 'ld-linux.so.3')
def pathToTuple(path, prefix = None):
    name = path.split(':')[0]
    if prefix is None:
        home_split = name.split('/./')
    else:
        home_split = [prefix, path.replace(prefix, '')]
    home = None
    if (len(home_split) == 2):
        home = home_split[0]
        name = home_split[1]
    return (home, name)

def createWordCount(codes):
    word_count = defaultdict(list)
    for code in codes:
        word_count[pathToTuple(code['line'])] += [code['walk']]
    return { k: sum(v) for k,v in word_count.items() }

def getRootNode(root_list, work_dir):
    root_node = list(filter(lambda node: node.name == work_dir, root_list))
    if (len(root_node)):
        # Found root node
        node = root_node[0]
    else:
        # Default constructor
        node = Node(work_dir, parent = None, value = 0, id = next_id())
        root_list.append(node)
    return node

def parse(codes):
    word_count = createWordCount(codes)

    resolver = Resolver('name')

    # Resolver cannot solve a name with path, thus, a root_list is required
    root_list = []
    for (work_dir,rel_path),times in word_count.items():
        work_dir = work_dir or '/unknown'

        node = getRootNode(root_list, work_dir)
        for path in rel_path.split('/'):
            node.value += times
            try:
                node = resolver.get(node, path)
            except anytree.resolver.ChildResolverError:
                node = Node(path, parent = node, value = times, id = next_id())

    tree_map = []
    for root in root_list:
        for node in anytree.PostOrderIter(root):
            # print("/".join([n.name for n in node.path]))
            parent_id = None if node.parent is None else str(node.parent.id)
            tree_map += [{
                    'id': str(node.id),
                    'parent': parent_id,
                    'name': node.name,
                    'value': node.value,
                }]

    return tree_map
