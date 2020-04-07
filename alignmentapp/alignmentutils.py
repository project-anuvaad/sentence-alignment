#!/bin/python
import codecs
import requests
import numpy as np
import csv
import random

from scipy.spatial import distance

two_files = True
no_of_words = 200
file_encoding = 'utf-16'


class AlignmentUtils:

    def __init__(self):
        pass

    def parse_csv(self, path_eng, path_indic, source, target_corp):
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