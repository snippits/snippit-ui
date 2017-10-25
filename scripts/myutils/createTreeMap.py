# Copyright (c) 2017, Medicine Yeh
import os
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
# Case 1 (Normal situations)
# From : /home/medicineyeh/Projects/qemu_arm_image/matrix_mul.c:36
# To   : ('/home/medicineyeh/Projects/qemu_arm_image', 'matrix_mul.c')
# Case 2 (Only happens when manually specify the relative path)
# From : /home/medicineyeh/Projects/qemu_arm_image/./matrix_mul.c:36
# To   : ('/home/medicineyeh/Projects/qemu_arm_image', 'matrix_mul.c')
# Case 3 (Only happens when it is a library/binary that has no DWARF)
# From : ld-linux.so.3
# To   : ('None', 'ld-linux.so.3')
def pathToTuple(path, prefix = None):
    name = path.split(':')[0]
    name = name.replace('/./', '/')
    return os.path.split(name)

def createWordCount(codes):
    word_count = defaultdict(list)
    for code in codes:
        word_count[pathToTuple(code['line'])] += [code['walk']]
    return { k: sum(v) for k,v in word_count.items() }

def parse(codes):
    word_count = createWordCount(codes)

    resolver = Resolver('name')

    # Resolver cannot solve a name with path, thus, a root_list is required
    root_node = Node('all', parent = None, value = 0, id = next_id())
    for (path,filename),times in word_count.items():
        path = path or '/unknown'
        path = path[1:] # Remove the leading slash
        path += '/' + filename

        node = root_node
        for name in path.split('/'):
            node.value += times
            try:
                node = resolver.get(node, name)
            except anytree.resolver.ChildResolverError:
                node = Node(name, parent = node, value = times, id = next_id())

    tree_map = []
    for node in anytree.PreOrderIter(root_node):
        # print("/".join([n.name for n in node.path]))
        if (node == root_node): continue
        if (node.parent == root_node):
            parent_id = None
        else:
            parent_id = str(node.parent.id)
        tree_map += [{
                'id': str(node.id),
                'parent': parent_id,
                'name': node.name,
                'value': node.value,
            }]

    return tree_map
