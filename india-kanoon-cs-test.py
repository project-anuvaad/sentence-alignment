#!/bin/python
import codecs
import copy

import requests
import numpy as np
import csv
import random

source = []
target_corp = []

no_of_words = 200
count_random = 2
file_encoding = 'utf-16'


def parse_csv():
    path = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Input\actual\src-ik-en.txt'
    path_indic = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Input\actual\target-ik-hi.txt'

    with codecs.open(path, 'r', file_encoding) as txt_file:
            for row in txt_file:
                if len(row.rstrip()) != 0:
                    source.append(row.rstrip())
    with codecs.open(path_indic, 'r', file_encoding) as txt_file:
            for row in txt_file:
                if len(row.rstrip()) != 0:
                    target_corp.append(row.rstrip())


def post_process_input(word_count):
    source[:] = [line for line in source if (len(line.split()) < word_count)]


def write_dict_to_csv(list, path):
    with codecs.open(path, 'w', file_encoding) as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in list:
            csv_writer.writerow(row)


def get_vect(query_in, lang, address='127.0.0.1:8050'):
    url = "http://" + address + "/vectorize"
    params = {"q": query_in, "lang": lang}
    resp = requests.get(url=url, params=params).json()
    return resp["embedding"]


def build_index():
    for sentence in source:
        source_embeddings.append(get_vect(sentence, lang='en'))
    for sentence in target_corp:
        target_embeddings.append(get_vect(sentence, lang='hi'))


def cscalc(vector_one, vector_two):
    vector_one = np.squeeze(vector_one)
    vector_two = np.squeeze(vector_two)
    dot = np.dot(vector_one, vector_two)
    norma = np.linalg.norm(vector_one)
    normb = np.linalg.norm(vector_two)
    cos = dot / (norma * normb)
    return cos


def get_target_sentence(index):
    cs = cscalc(source_embeddings[index], target_embeddings[index])
    return i, cs


def get_randomindexes(curr_index):
    rand_list = list(range(1, curr_index)) + list(range(curr_index+1, len(target_embeddings)))
    return random.sample(rand_list, count_random)


def get_mismatch_index(target_embeddings, source_embedding, source_index):
    cs_mismatch = {}
    random_indexes = get_randomindexes(source_index)
    for index in random_indexes:
        cs = cscalc(source_embedding, target_embeddings[index])
        cs_mismatch[index] = cs
    return cs_mismatch


embedded_dict = {}
mismatch_dict = {}
mismatch_output = []
similarity_out = []
source_embeddings = []
target_embeddings = []

parse_csv()
build_index()

for i, embeddings in enumerate(source_embeddings):
    i, dist = get_target_sentence(i)
    if dist < 0.6:
        embedded_dict[i] = get_target_sentence(i)
    internal_dict = get_mismatch_index(target_embeddings, embeddings, i)
    false_postives = {}
    for key in internal_dict:
        if internal_dict[key] >= 0.6:
            false_postives[key] = internal_dict[key]
    mismatch_dict[i] = false_postives

for key in embedded_dict:
    tup = str(source[key]) + " |||| " + str(target_corp[embedded_dict[key][0]]), " ||||| " + str(embedded_dict[key][1])
    similarity_out.append(tup)

for key in mismatch_dict:
    for internal_key in mismatch_dict[key]:
        tup = str(source[key]) + " |||| " + str(target_corp[internal_key]),  " ||||| " + str(mismatch_dict[key][internal_key])
        mismatch_output.append(tup)

mismatch_output = sorted(mismatch_output, key = lambda x:x[1], reverse = True)


out_path = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Result\mismatch.txt'
similarity_path = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Result\similarity.txt'

write_dict_to_csv(mismatch_output, out_path)
write_dict_to_csv(similarity_out, similarity_path)