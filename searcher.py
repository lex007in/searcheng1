import pickle
import sys
import re

__author__ = 'ivannik'


def validate_prompt(user_input):
    if re.fullmatch(r'[A-Za-zА-Яа-яё\d-]+(\sAND\s[A-Za-zА-Яа-яё\d-]+)*', user_input):
        return False, user_input.split(' AND ')
    elif re.fullmatch(r'[A-Za-zА-Яа-яё\d-]+(\sOR\s[A-Za-zА-Яа-яё\d-]+)*', user_input):
        return True, user_input.split(' OR ')
    else:
        return None, None


def search(index, words, is_or):
    if is_or:
        documents = set()
        for word in words:
            documents = documents.union(index.get(word, set()))
        return list(documents)
    else:
        documents = set(index.get(words[0], set()))
        for word in words:
            documents = documents.intersection(index.get(word, set()))
        return list(documents)


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
        (is_or, query_words) = validate_prompt(userInput)
        if query_words is None:
            print('incorrect query')
            continue
        doc_indexes = search(search_index, query_words, is_or)
        print_results(files_list, doc_indexes)
