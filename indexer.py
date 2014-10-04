import sys
import os
import re
import pymorphy2
import pickle

__author__ = 'ivannik'

morph = pymorphy2.MorphAnalyzer()


def index_dir(dir_name):
    search_index = {}
    filename_list = []
    global_file_index = 0
    for root_dir, dirs, files in os.walk(dir_name):
        for file in files:
            file_path = os.path.normpath(os.path.join(root_dir, file))
            filename_list.append(file_path)
            with open(file_path, encoding='UTF-8') as f:
                processed = set()
                for l, line in enumerate(f):
                    for token in re.finditer(re.compile(r'[A-Za-zА-Яа-яё\\d-]+'), line):
                        if token.group(0) not in processed:
                            processed.add(token.group(0))
                            for term in set([t.normal_form for t in morph.parse(token.group(0))]):
                                if term not in search_index:
                                    search_index[term] = set()
                                search_index[term].add(global_file_index)
                print('file ' + file_path + ' processed')
                global_file_index += 1
    return search_index, filename_list


index, file_indexes = index_dir(sys.argv[1])
with open(sys.argv[2], 'wb') as index_file:
    pickle.dump((file_indexes, index), index_file)