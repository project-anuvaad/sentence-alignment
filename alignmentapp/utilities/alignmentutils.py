#!/bin/python
import binascii
import codecs
import json
import os

import requests
import numpy as np
import csv
import random

from scipy.spatial import distance

two_files = os.environ.get('TWO_FILES', True)
no_of_words = os.environ.get('WORD_LENGTH', 200)
file_encoding = os.environ.get('FILE_ENCODING', 'utf-16')
upload_url = os.environ.get('FILE_UPLOAD_URL', 'http://auth.anuvaad.org/upload')

class AlignmentUtils:

    def __init__(self):
        pass

    def parse_input_file(self, path_eng, path_indic, source, target_corp):
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


    def write_output(self, list, path):
        with codecs.open(path, 'w', file_encoding) as txt_file:
            for row in list:
                txt_file.write(row + "\r\n")


    def cscalc(self, vector_one, vector_two):
        vector_one = np.squeeze(vector_one)
        vector_two = np.squeeze(vector_two)
        dot = np.dot(vector_one, vector_two)
        norma = np.linalg.norm(vector_one)
        normb = np.linalg.norm(vector_two)
        cos = dot / (norma * normb)
        return cos

    def post_process_input(self, word_count, source):
        source[:] = [line for line in source if (len(line.split()) < word_count)]

    def convert_file_to_binary(self, file_path):
        x = ""
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(32), b''):
                x += str(binascii.hexlify(chunk)).replace("b", "").replace("'", "")
        b = bin(int(x, 16)).replace('b', '')
        return b

    def upload_file_binary(self, file):
        data = open(file, 'rb')
        response = requests.post(url = upload_url, data = data,
                                 headers = {'Content-Type': 'application/x-www-form-urlencoded'})
        data = json.loads(response.text)
        for key, value in data.items():
            if key == "data":
                return value["filepath"]


    def get_cs_on_sen_cat(self, sentence):
        sen_len = len(sentence.split())
        if 0 < sen_len <= 10:
            #SMALL
            return 0.7, 0.75
        elif 10 < sen_len <= 20:
            #MEDIUM
            return 0.75, 0.8
        else:
            #LARGE
            return 0.75, 0.8
