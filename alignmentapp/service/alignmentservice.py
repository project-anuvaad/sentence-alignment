#!/bin/python
import codecs
import os

import numpy as np
from scipy.spatial import distance
from flask import jsonify
from laser.laser import Laser
from utilities.alignmentutils import AlignmentUtils

directory_path = os.environ.get('DIRECTORY_PATH', r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Input')
res_suffix = 'response-'
alignmentutils = AlignmentUtils()
laser = Laser()


class AlignmentService:
    def __init__(self):
        pass

    def validate_input(self, data):
        if 'source' not in data.keys():
            return self.get_error("SOURCE_NOT_FOUND", "Details of the source not available")
        else:
            source = data["source"]
            if 'filepath' not in source.keys():
                return self.get_error("SOURCE_FILE_NOT_FOUND", "Details of the source file not available")
            elif 'locale' not in source.keys():
                return self.get_error("SOURCE_LOCALE_NOT_FOUND", "Details of the source locale not available")
        if 'target' not in data.keys():
            return self.get_error("TARGET_NOT_FOUND", "Details of the target not available")
        else:
            target = data["target"]
            if 'filepath' not in target.keys():
                return self.get_error("TARGET_FILE_NOT_FOUND", "Details of the target file not available")
            elif 'locale' not in target.keys():
                return self.get_error("TARGET_LOCALE_NOT_FOUND", "Details of the target locale not available")

    def get_error(self, code, message):
        return jsonify({"status": "ERROR", "code": code, "message": message})

    def build_index(self, source, target_corp):
        source_embeddings = [laser.get_vect(sentence, lang='en') for sentence in source]
        target_embeddings = [laser.get_vect(sentence, lang='hi') for sentence in target_corp]

        return source_embeddings, target_embeddings

    def get_target_sentence(self, target_embeddings, source_embedding, src_sent):
        data = np.array(target_embeddings)
        data = data.reshape(data.shape[0], data.shape[2])
        distances = distance.cdist(np.array(source_embedding), data, "cosine")[0]
        min_index = np.argmin(distances)
        min_distance = 1 - distances[min_index]
        cs = alignmentutils.get_cs_on_sen_cat(src_sent)
        if min_distance >= cs:
            return min_index, min_distance

    def process(self, path, path_indic):
        embedded_dict = {}
        source_reformatted = []
        target_refromatted = []
        source = []
        target_corp = []
        lines_with_no_match = []
        full_path = directory_path + '/' + path
        full_path_indic = directory_path + '/' + path_indic

        alignmentutils.parse_csv(full_path, full_path_indic, source, target_corp)
        source_embeddings, target_embeddings = self.build_index(source, target_corp)

        for i, embedding in enumerate(source_embeddings):
            trgt = self.get_target_sentence(target_embeddings, embedding, source[i])
            if trgt is not None:
                embedded_dict[i] = trgt
            else:
                lines_with_no_match.append(source[i])

        for key in embedded_dict:
            source_reformatted.append(source[key])
            target_refromatted.append(target_corp[embedded_dict[key][0]])

        output_dict = self.generate_output(source_reformatted, target_refromatted, path, path_indic)

        return jsonify({"status": "Success",
                        "inputFiles": path + " | " + path_indic,
                        "sourceOutput": output_dict["source"],
                        "targetOutput": output_dict["target"]})

    def generate_output(self, source_reformatted, target_refromatted, path, path_indic):
        output_source = directory_path + '/' + res_suffix + path
        output_target = directory_path + '/' + res_suffix + path_indic
        alignmentutils.write_output(source_reformatted, output_source)
        alignmentutils.write_output(target_refromatted, output_target)
        return self.get_response_paths(output_source, output_target)

    def get_response_paths(self, output_src, output_trgt):
        output_src = alignmentutils.upload_file_binary(output_src)
        output_trgt = alignmentutils.upload_file_binary(output_trgt)
        output_dict = {"source": output_src, "target": output_trgt}
        return output_dict
