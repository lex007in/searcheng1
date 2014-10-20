from collections import defaultdict
import pickle
import sys
import re
import enum

__author__ = 'ivannik'


class QueryType(enum.Enum):
    q_or = 1
    q_and = 2
    q_distance = 3


def doc():
    return defaultdict(list)


def validate_prompt(user_input):
    if re.fullmatch(r'[A-Za-zА-Яа-яё\d-]+(\sAND\s[A-Za-zА-Яа-яё\d-]+)*', user_input):
        return QueryType.q_and, user_input.split(' AND ')
    elif re.fullmatch(r'[A-Za-zА-Яа-яё\d-]+(\sOR\s[A-Za-zА-Яа-яё\d-]+)*', user_input):
        return QueryType.q_or, user_input.split(' OR ')
    elif re.fullmatch(r'[A-Za-zА-Яа-яё\d-]+(\s/[+-]?\d+\s[A-Za-zА-Яа-яё\d-]+)*', user_input):
        return QueryType.q_distance, user_input.split(' ')
    else:
        return None, None


def pos_intersect(p_1, p_2, k):
    documents = defaultdict(list)

    if k.startswith("/+"):
        dist = lambda x: x
    elif k.startswith("/-"):
        dist = lambda x: x
    else:
        dist = abs

    k_int = int(k[1:])
    common_docs = set(p_1.keys()).intersection(set(p_2.keys()))
    for doc in common_docs:
        i1 = 0
        i2 = 0
        while i1 < len(p_1[doc]) and i2 < len(p_2[doc]):
            if dist(p_1[doc][i1] - p_2[doc][i2]) <= k_int:
                documents[doc].append(p_1[doc][i1])
                i1 += 1
            elif p_1[doc][i1] < p_2[doc][i2]:
                i1 += 1
            else:
                i2 += 1
    return documents


def search(index, words, query_type):
    if query_type == QueryType.q_or:
        documents = set()
        for word in words:
            documents = documents.union(index[word].keys())
        return list(documents)
    elif query_type == QueryType.q_and:
        documents = set(index.get(words[0], set()))
        for word in words:
            documents = documents.intersection(index[word].keys())
        return list(documents)
    elif query_type == QueryType.q_distance:
        documents = index.get(words[0], defaultdict(list))
        if len(words) < 3:
            # never happen
            return list(documents.keys())
        for i in range(2, len(words), 2):
            documents = pos_intersect(documents, index.get(words[i], defaultdict(list)), words[i - 1])
        return list(documents.keys())


def print_results(file_names, file_indexes):
    if len(file_indexes) == 0:
        print('no documents found')
    elif len(file_indexes) <= 2:
        found = [file_names[i] for i in file_indexes]
        print('found ' + ", ".join(found))
    else:
        found = [file_names[i] for i in file_indexes[:2]]
        print('found ' + ", ".join(found) + ' and ' + str(len(file_indexes) - 2) + ' more')


with open(sys.argv[1], 'rb') as index_file:
    files_list, search_index = pickle.load(index_file)
    print("type 'q' to exit")
    while True:
        userInput = input('search: ')
        if userInput == 'q':
            break
        (q_type, query_words) = validate_prompt(userInput)
        if q_type is None:
            print('incorrect query')
            continue
        doc_indexes = search(search_index, query_words, q_type)
        print_results(files_list, doc_indexes)
