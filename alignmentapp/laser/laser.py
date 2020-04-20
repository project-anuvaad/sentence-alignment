#!/bin/python
import os
from collections import OrderedDict
from functools import partial

import requests
import multiprocessing

laser_url = os.environ.get('LASER_PATH', 'http://127.0.0.1:8050/vectorize')
no_of_processes = os.environ.get('NO_OF_PROCESSES', 5)

class Laser:

    def __init__(self):
        pass

    def get_vect(self, query_tuple, lang):
        query_in = query_tuple[1]
        params = {"q": query_in, "lang": lang}
        resp = requests.get(url=laser_url, params=params).json()
        return query_tuple[0], resp["embedding"]

    def vecotrize_sentences(self, source, target):
        pool = multiprocessing.Pool(no_of_processes)
        processed_source = self.convert_to_list_of_tuples(source)
        func = partial(self.get_vect, lang ="en")
        source_list = pool.map(func, processed_source)
        processed_target = self.convert_to_list_of_tuples(target)
        func = partial(self.get_vect, lang = "hi")
        target_list = pool.map(func, processed_target)
        pool.close()
        return self.align_lists(source_list, target_list)

    def convert_to_list_of_tuples(self, list):
        final_list = []
        for i, line in enumerate(list):
            tup = i, line
            final_list.append(tup)
        return final_list

    def align_lists(self, source, target):
        source_emb = list(OrderedDict(sorted(dict(source).items())).values())
        trgt_emb = list(OrderedDict(sorted(dict(target).items())).values())
        return source_emb, trgt_emb

