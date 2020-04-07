#!/bin/python
import codecs

import numpy as np
from scipy.spatial import distance
from flask import jsonify
from .laser import Laser
from alignmentapp.alignmentutils import AlignmentUtils

p = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Input\src-ik-en.txt'
p_indic = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Input\target-ik-hi.txt'

source_enu = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Result\source-enu.txt'
target_enu = r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Result\target-enu.txt'

alignmentutils = AlignmentUtils()
laser = Laser()

class AlignmentService:
    def __init__(self):
        pass

    def build_index(self, source_embeddings, target_embeddings, source, target_corp):
        for sentence in source:
            source_embeddings.append(laser.get_vect(sentence, lang='en'))
        for sentence in target_corp:
            target_embeddings.append(laser.get_vect(sentence, lang='hi'))

    def get_target_sentence(self, target_embeddings, source_embedding):
        data = np.array(target_embeddings)
        data = data.reshape(data.shape[0], data.shape[2])
        distances = distance.cdist(np.array(source_embedding), data, "cosine")[0]
        min_index = np.argmin(distances)
        min_distance = 1 - distances[min_index]
        return min_index, min_distance

    def process(self, path, path_indic):
        embedded_dict = {}
        source_reformatted = []
        target_refromatted = []
        source_embeddings = []
        target_embeddings = []
        source = []
        target_corp = []

        print(path)
        print(path_indic)

        alignmentutils.parse_csv(p, p_indic, source, target_corp)
        self.build_index(source_embeddings, target_embeddings, source, target_corp)

        for i, embeddings in enumerate(source_embeddings):
            embedded_dict[i] = self.get_target_sentence(target_embeddings, embeddings)

        for key in embedded_dict:
            source_reformatted.append(source[key])
            target_refromatted.append(target_corp[embedded_dict[key][0]])

        self.generate_output(source_reformatted, target_refromatted)

        return jsonify({"Status": "Success", "File": "ABC"})


    def generate_output(self, source_reformatted, target_refromatted):
        alignmentutils.write_dict_to_csv(source_reformatted, source_enu)
        alignmentutils.write_dict_to_csv(target_refromatted, target_enu)