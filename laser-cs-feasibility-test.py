#!/bin/python
import codecs

import requests
import numpy as np
import csv
import random

from scipy.spatial import distance


source = []
target_corp = []

two_files = True
no_of_words = 200
count_random = 3

def parse_csv():
    path = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Input\src-ik-en.txt'
    path_indic = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Input\target-ik-hi.txt'
    if two_files:
        with codecs.open(path, 'r', 'utf-8-sig') as txt_file:
            for row in txt_file:
                if len(row.rstrip()) != 0:
                    source.append(row.rstrip())
        with codecs.open(path_indic, 'r', 'utf-8-sig') as txt_file:
            for row in txt_file:
                if len(row.rstrip()) != 0:
                    target_corp.append(row.rstrip())

    else:
        with codecs.open(path, 'r', 'utf-16') as csv_file:
            csv_reader = csv.reader((l.replace('\0', '') for l in csv_file))
            for row in csv_reader:
                if len(row) != 0:
                    source.append(row[0])
                    target_corp.append(row[1])


def post_process_input(word_count):
    source[:] = [line for line in source if (len(line.split()) < word_count)]


def write_dict_to_csv(list, path):
    with codecs.open(path, 'w', 'utf-16') as csv_file:
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


def get_target_sentence(target_embeddings, source_embedding):
    data = np.array(target_embeddings)
    data = data.reshape(data.shape[0], data.shape[2])
    distances = distance.cdist(np.array(source_embedding), data, "cosine")[0]
    min_index = np.argmin(distances)
    min_distance = 1 - distances[min_index]

    return min_index, min_distance


def get_mismatch_index(target_embeddings, source_embedding):
    cs_mismatch = {}
    random_indexes = random.sample(range(1, len(target_embeddings)), count_random)
    for index in random_indexes:
        cs = cscalc(source_embedding, target_embeddings[index])
        cs_mismatch[index] = cs

    return cs_mismatch


embedded_dict = {}
mismatch_dict = {}
source_reformatted = []
target_refromatted = []

mismatch_output = []
similarity_out = []


source_embeddings = []
target_embeddings = []

parse_csv()
build_index()

for i, embeddings in enumerate(source_embeddings):
    embedded_dict[i] = get_target_sentence(target_embeddings, embeddings)
    mismatch_dict[i] = get_mismatch_index(target_embeddings, embeddings)

for key in embedded_dict:
    tup = str(key) + "|" + str(embedded_dict[key][0]), " " + str(embedded_dict[key][1])
    similarity_out.append(tup)

for key in mismatch_dict:
    for internal_key in mismatch_dict[key]:
        tup = str(key) + " | " + str(internal_key),  "   " + str(mismatch_dict[key][internal_key])
        mismatch_output.append(tup)

mismatch_output = sorted(mismatch_output, key = lambda x:x[1], reverse = True)

for j, sentence in enumerate(source):
    tup = j, sentence
    source_reformatted.append(tup)

for j, sentence in enumerate(target_corp):
    tup = j, sentence
    target_refromatted.append(tup)

out_path = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Result\mismatch.txt'
similarity_path = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Result\similarity.txt'
source_enu = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Result\source-enu.txt'
target_enu = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Result\target-enu.txt'

write_dict_to_csv(mismatch_output, out_path)
write_dict_to_csv(similarity_out, similarity_path)
write_dict_to_csv(source_reformatted, source_enu)
write_dict_to_csv(target_refromatted, target_enu)