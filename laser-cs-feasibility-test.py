#!/bin/python
import codecs

import requests
import numpy as np
import csv
import random

from scipy.spatial import distance


source = []
target_corp = []

processed_src = []
processed_trgt = []

two_files = True
word_count_min = 0
word_count_max_incl = 20
count_random = 10
file_encoding = 'utf-16'


def parse_csv(path_eng, path_indic):
    if two_files:
        with codecs.open(path_eng, 'r', file_encoding) as txt_file:
            for row in txt_file:
                if len(row.rstrip()) != 0:
                    source.append(row.rstrip())
        with codecs.open(path_indic, 'r', file_encoding) as txt_file:
            for row in txt_file:
                if len(row.rstrip()) != 0:
                    target_corp.append(row.rstrip())

    else:
        with codecs.open(path_eng, 'r', file_encoding) as csv_file:
            csv_reader = csv.reader((l.replace('\0', '') for l in csv_file))
            for row in csv_reader:
                if len(row) != 0:
                    source.append(row[0])
                    target_corp.append(row[1])


def post_process_input():
    source[:] = [line for line in source if ((len(line.split()) <= word_count_max_incl) and (len(line.split()) > word_count_min))]
    #target_corp[:] = [line for line in target_corp if (len(line.split()) < no_of_words)]


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


def build_index(source_embeddings, target_embeddings):
    source_embeddings = [get_vect(sentence, lang='en') for sentence in source]
    target_embeddings = [get_vect(sentence, lang='hi') for sentence in target_corp]

    return source_embeddings, target_embeddings

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


def process(path, path_indic):
    embedded_dict = {}
    mismatch_dict = {}
    source_reformatted = []
    target_refromatted = []
    mismatch_output = []
    similarity_out = []
    source_embeddings = []
    target_embeddings = []

    parse_csv(path, path_indic)
    post_process_input()
    print("Processed source length: ", len(source))
    print("Processed target length: ", len(target_corp))
    source_embeddings, target_embeddings = build_index(source_embeddings, target_embeddings)

    for i, embeddings in enumerate(source_embeddings):
        embedded_dict[i] = get_target_sentence(target_embeddings, embeddings)
        mismatch_dict[i] = get_mismatch_index(target_embeddings, embeddings)

    for key in embedded_dict:
        tup = str(key) + "|" + str(embedded_dict[key][0]), " " + str(embedded_dict[key][1])
        similarity_out.append(tup)

    for key in mismatch_dict:
        for internal_key in mismatch_dict[key]:
            tup = str(key) + " | " + str(internal_key), "   " + str(mismatch_dict[key][internal_key])
            mismatch_output.append(tup)

    mismatch_output = sorted(mismatch_output, key=lambda x: x[1], reverse=True)
    generate_output(source_reformatted, target_refromatted, mismatch_output, similarity_out)


def generate_output(source_reformatted, target_refromatted, mismatch_output, similarity_out):
    for j, sentence in enumerate(source):
        tup = j, sentence
        source_reformatted.append(tup)

    for j, sentence in enumerate(target_corp):
        tup = j, sentence
        target_refromatted.append(tup)

    write_dict_to_csv(mismatch_output, out_path)
    write_dict_to_csv(similarity_out, similarity_path)
    write_dict_to_csv(source_reformatted, source_enu)
    write_dict_to_csv(target_refromatted, target_enu)



p = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Input\actual\src-ik-en.txt'
p_indic = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Input\actual\target-ik-hi.txt'

out_path = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Result\mismatch.txt'
similarity_path = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Result\similarity.txt'
source_enu = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Result\source-enu.txt'
target_enu = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Result\target-enu.txt'

process(p, p_indic)

print("Done.")