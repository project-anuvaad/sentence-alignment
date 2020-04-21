#!/bin/python
import codecs
import os

import numpy as np
import datetime as dt
from scipy.spatial import distance
from flask import jsonify
from laser.laser import Laser
from utilities.alignmentutils import AlignmentUtils
from repository.alignmentrepository import AlignmentRepository
from kafkawrapper.producer import Producer

directory_path = os.environ.get('DIRECTORY_PATH', r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Input')
res_suffix = 'response-'
man_suffix = 'manual-'
nomatch_suffix = 'nomatch-'
file_path_delimiter = os.environ.get('FILE_PATH_DELIMITER', '\\')
alignmentutils = AlignmentUtils()
repo = AlignmentRepository()
laser = Laser()
producer = Producer()

class AlignmentService:
    def __init__(self):
        pass

    def register_job(self, object):
        repo.create_job(object)
        print(str(dt.datetime.now()) + " : JOB ID: ", object["jobID"])
        #producer.push_to_queue(object)

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
        source_embeddings, target_embeddings = laser.vecotrize_sentences(source, target_corp)
        return source_embeddings, target_embeddings

    def get_target_sentence(self, target_embeddings, source_embedding, src_sent):
        data = np.array(target_embeddings)
        data = data.reshape(data.shape[0], data.shape[2])
        distances = distance.cdist(np.array(source_embedding), data, "cosine")[0]
        min_index = np.argmin(distances)
        min_distance = 1 - distances[min_index]
        min_cs, max_cs = alignmentutils.get_cs_on_sen_cat(src_sent)
        if min_distance >= max_cs:
            return min_index, min_distance, "MATCH"
        elif min_cs <= min_distance < max_cs:
            return min_index, min_distance, "MANUAL"

    def process(self, object):
        match_dict = {}
        manual_dict = {}
        source_reformatted = []
        target_refromatted = []
        manual_src = []
        manual_trgt = []
        lines_with_no_match = []
        path = object["source"]
        path_indic = object["target"]
        full_path = directory_path + file_path_delimiter + path
        full_path_indic = directory_path + file_path_delimiter + path_indic
        object["status"] = "INPROGRESS"
        object["startTime"] = str(dt.datetime.now())
        repo.update_job(object, object["jobID"])
        source, target_corp = alignmentutils.parse_input_file(full_path, full_path_indic)
        source_embeddings, target_embeddings = self.build_index(source, target_corp)
        for i, embedding in enumerate(source_embeddings):
            trgt = self.get_target_sentence(target_embeddings, embedding, source[i])
            if trgt is not None:
                if trgt[2] is "MATCH":
                    match_dict[i] = trgt[0], trgt[1]
                else:
                    manual_dict[i] = trgt[0], trgt[1]
            else:
                lines_with_no_match.append(source[i])
        for key in match_dict:
            source_reformatted.append(source[key])
            target_refromatted.append(target_corp[match_dict[key][0]])
        print(str(dt.datetime.now()) + " : Match Bucket Filled...")
        if len(manual_dict.keys()) > 0:
            for key in manual_dict:
                manual_src.append(source[key])
                manual_trgt.append(target_corp[manual_dict[key][0]])
        print(str(dt.datetime.now()) + " : Manual Bucket Filled...")
        print(str(dt.datetime.now()) + " : No Match Bucket Filled...")
        output_dict = self.generate_output(source_reformatted, target_refromatted, manual_src, manual_trgt,
                                           lines_with_no_match, path, path_indic)
        result = self.build_final_response(path, path_indic, output_dict, object)
        repo.update_job(result, object["jobID"])
        return jsonify(result)

    def generate_output(self, source_reformatted, target_refromatted, manual_src, manual_trgt, nomatch_src, path, path_indic):
        output_source = directory_path + file_path_delimiter + res_suffix + path
        output_target = directory_path + file_path_delimiter + res_suffix + path_indic
        output_manual_src = directory_path + file_path_delimiter + man_suffix + path
        output_manual_trgt = directory_path + file_path_delimiter + man_suffix + path_indic
        output_nomatch = directory_path + file_path_delimiter + nomatch_suffix + path
        alignmentutils.write_output(source_reformatted, output_source)
        alignmentutils.write_output(target_refromatted, output_target)
        alignmentutils.write_output(manual_src, output_manual_src)
        alignmentutils.write_output(manual_trgt, output_manual_trgt)
        alignmentutils.write_output(nomatch_src, output_nomatch)
        return self.get_response_paths(output_source, output_target,
                                       output_manual_src, output_manual_trgt, output_nomatch)


    def get_response_paths(self, output_src, output_trgt, output_manual_src, output_manual_trgt, output_nomatch):
        output_src = alignmentutils.upload_file_binary(output_src)
        output_trgt = alignmentutils.upload_file_binary(output_trgt)
        output_manual_src = alignmentutils.upload_file_binary(output_manual_src)
        output_manual_trgt = alignmentutils.upload_file_binary(output_manual_trgt)
        output_nomatch = alignmentutils.upload_file_binary(output_nomatch)
        output_dict = {"source": output_src, "target": output_trgt, "manual_src": output_manual_src,
                       "manual_trgt": output_manual_trgt, "nomatch": output_nomatch }
        return output_dict

    def build_final_response(self, source, target, output, object):
        result = {"status": "COMPLETED",
                  "jobID": object["jobID"],
                  "startTime": object["start_time"],
                  "endTime": str(dt.datetime.now()),
                  "input": {
                      "source": source,
                      "target": target
                  },
                  "output": {
                      "aligned": {
                          "source": output["source"],
                          "target": output["target"]
                      },
                      "manual": {
                          "source": output["manual_src"],
                          "target": output["manual_trgt"]
                      },
                      "nomatch": {
                          "source": output["nomatch"]
                      }
                  }}

        return result

    def search_jobs(self, job_id):
        return repo.search_job(job_id)


