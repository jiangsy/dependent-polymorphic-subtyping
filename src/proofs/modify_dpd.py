from pathlib import Path
import re
import copy

def get_coqfiles(file_names):
    if len(file_names) == 0:    
        file_names = list(Path(".").rglob("*.[vV]"))
    file_names = list(map(lambda x: str(x), file_names))
    return list(map(lambda x: x[:-2], file_names))


def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dpd_file', type=str, default='graph.dpd')
    parser.add_argument('--coq_files', nargs='+', default=[])
    args = parser.parse_args()
    return args


def get_node_indicies(contents, coq_files):
    node_contents = filter(lambda x: x.startswith('N: '), contents)
    all_node_indices = []
    unused_node_indices = []
    for node in node_contents:
        match_res = re.match('N: (\d*) .*', node)
        assert match_res is not None
        node_index = int(match_res.group(1))
        all_node_indices.append(node_index)
        match_res = re.match('.*path="(.*)"', node)
        if match_res is None or not match_res.group(1) in coq_files or match_res.group(1) == 'Language':
            unused_node_indices.append(node_index)
    assert len(list(set(all_node_indices))) == len(all_node_indices)
    all_node_indices.sort()
    assert all_node_indices[-1] == len(all_node_indices)
    unused_node_indices.sort()
    print(unused_node_indices)
    return all_node_indices, unused_node_indices


def reindex(all_node_indices, unused_node_indices):
    left_indices = set(all_node_indices).difference(unused_node_indices)
    left_indices = list(left_indices)
    left_indices.sort()
    reindex_map = {ori_index: new_index for (ori_index, new_index) in zip(left_indices, range(1, 1+len(left_indices)))}
    return reindex_map


def modifiy_dpd(dpd_file, coq_files):
    with open(dpd_file, 'r') as f:
        contents = f.readlines()
    all_node_indices, unused_node_indices = get_node_indicies(copy.deepcopy(contents), coq_files)
    reindex_map = reindex(all_node_indices, unused_node_indices)
    with open('new_' + dpd_file, 'w') as f:
        for content in contents:
            if content.startswith('N: '):
                match_res = re.match('N: (\d*) .*', content)
                node_index = int(match_res.group(1))
                node_index_span = match_res.span(1)
                if not (node_index in unused_node_indices): 
                    f.write(content[:node_index_span[0]] + str(reindex_map[node_index]) + content[node_index_span[1]:])
            elif content.startswith('E: '):
                match_res = re.match('E: (\d*) (\d*) .*', content)
                node1_index = int(match_res.group(1))
                node1_index_span = match_res.span(1)
                node2_index = int(match_res.group(2))
                node2_index_span = match_res.span(2)
                if (not node1_index in unused_node_indices) and (not node2_index in unused_node_indices):
                    f.write(content[:node1_index_span[0]] + str(reindex_map[node1_index]) + content[node1_index_span[1]:node2_index_span[0]] + str(reindex_map[node2_index]) + content[node2_index_span[1]:])
            else:
                assert False
    pass



if __name__ == '__main__':
    args = parse_args()

    dpd_file = args.dpd_file
    coq_files = get_coqfiles(args.coq_files)
    modifiy_dpd(dpd_file, coq_files)
    pass