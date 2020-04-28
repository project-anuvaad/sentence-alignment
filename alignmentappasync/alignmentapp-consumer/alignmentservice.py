#!/bin/python
import codecs
import logging
import os
import traceback
from logging.config import dictConfig

import numpy as np
import datetime as dt
from scipy.spatial import distance
from flask import jsonify
from laser.laser import Laser
from utilities.alignmentutils import AlignmentUtils
from repository.alignmentrepository import AlignmentRepository
from kafkawrapper.consumer import Consumer

log = logging.getLogger('file')
directory_path = os.environ.get('SA_DIRECTORY_PATH',
                                r'C:\Users\Vishal\Desktop\anuvaad\Facebook LASER\resources\Input\length-wise')
res_suffix = 'response-'
man_suffix = 'manual-'
nomatch_suffix = 'nomatch-'
file_path_delimiter = os.environ.get('FILE_PATH_DELIMITER', '/')
alignmentutils = AlignmentUtils()
repo = AlignmentRepository()
laser = Laser()
consumer = Consumer()

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] {%(filename)s:%(lineno)d} %(threadName)s %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {
        'info': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'filename': 'info.log'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'stream': 'ext://sys.stdout',
        }
    },
    'loggers': {
        'file': {
            'level': 'DEBUG',
            'handlers': ['info', 'console'],
            'propagate': ''
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['info', 'console']
    }
})


def build_index(source, target_corp):
    source_embeddings, target_embeddings = laser.vecotrize_sentences(source, target_corp)
    return source_embeddings, target_embeddings


def get_target_sentence(target_embeddings, source_embedding, src_sent):
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


def process():
    data = consume()
    if data is None:
        return None
    object_in = data
    log.info("Alignment process starts for job: " + str(object_in["jobID"]))
    source_reformatted = []
    target_refromatted = []
    manual_src = []
    manual_trgt = []
    path = object_in["source"]
    path_indic = object_in["target"]
    full_path = directory_path + file_path_delimiter + path
    full_path_indic = directory_path + file_path_delimiter + path_indic
    object_in["status"] = "INPROGRESS"
    object_in["startTime"] = str(dt.datetime.now())
    repo.update_job(object_in, object_in["jobID"])
    parsed_in = parse_in(full_path, full_path_indic, object_in)
    if parsed_in is not None:
        source = parsed_in[0]
        target_corp = parsed_in[1]
    else:
        return {}
    embeddings = build_embeddings(source, target_corp, object_in)
    if embeddings is not None:
        source_embeddings = embeddings[0]
        target_embeddings = embeddings[1]
    else:
        return {}
    alignments = get_alignments(source_embeddings, target_embeddings, source, object_in)
    if alignments is not None:
        match_dict = alignments[0]
        manual_dict = alignments[1]
        lines_with_no_match = alignments[2]
        for key in match_dict:
            source_reformatted.append(source[key])
            target_refromatted.append(target_corp[match_dict[key][0]])
        log.info("Match Bucket Filled.")
        if len(manual_dict.keys()) > 0:
            for key in manual_dict:
                manual_src.append(source[key])
                manual_trgt.append(target_corp[manual_dict[key][0]])
        log.info("Manual Bucket Filled.")
        log.info("No Match Bucket Filled.")
        output_dict = generate_output(source_reformatted, target_refromatted, manual_src, manual_trgt,
                                           lines_with_no_match, path, path_indic)
        result = build_final_response(path, path_indic, output_dict, object_in)
        repo.update_job(result, object_in["jobID"])
        log.info("Sentences aligned Successfully! JOB ID: " + str(object_in["jobID"]))
    else:
        return {}


def consume():
    con = consumer.get_consumer()
    try:
        for msg in con:
            log.info("Consuming from the Kafka Queue......")
            data = msg.value
            return data
    except Exception as e:
        log.error("Exception while consuming: " + str(e))
        log.error(str(traceback.print_exc()))
        return None


def parse_in(full_path, full_path_indic, object_in):
    try:
        source, target_corp = alignmentutils.parse_input_file(full_path, full_path_indic)
        return source, target_corp
    except Exception as e:
        log.error("Exception while parsing the input: " + str(e))
        log.error(str(traceback.print_exc()))
        update_job_status("FAILED", object_in, "Exception while parsing the input")
        return None


def build_embeddings(source, target_corp, object_in):
    try:
        source_embeddings, target_embeddings = build_index(source, target_corp)
        return source_embeddings, target_embeddings
    except Exception as e:
        log.error("Exception while vectorising sentences: " + str(e))
        log.error(str(traceback.print_exc()))
        update_job_status("FAILED", object_in, "Exception while vectorising sentences")
        return None


def get_alignments(source_embeddings, target_embeddings, source, object_in):
    match_dict = {}
    manual_dict = {}
    lines_with_no_match = []
    try:
        for i, embedding in enumerate(source_embeddings):
            trgt = get_target_sentence(target_embeddings, embedding, source[i])
            if trgt is not None:
                if trgt[2] is "MATCH":
                    match_dict[i] = trgt[0], trgt[1]
                else:
                    manual_dict[i] = trgt[0], trgt[1]
            else:
                lines_with_no_match.append(source[i])
        return match_dict, manual_dict, lines_with_no_match
    except Exception as e:
        log.error("Exception while aligning sentences: " + str(e))
        log.error(str(traceback.print_exc()))
        update_job_status("FAILED", object_in, "Exception while aligning sentences")
        return None


def update_job_status(status, object_in, cause):
    object_in["status"] = status
    object_in["endTime"] = str(dt.datetime.now())
    if cause is not None:
        object_in["cause"] = cause
    repo.update_job(object_in, object_in["jobID"])


def generate_output(source_reformatted, target_refromatted, manual_src, manual_trgt, nomatch_src, path,
                    path_indic):
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
    return get_response_paths(output_source, output_target,
                                   output_manual_src, output_manual_trgt, output_nomatch)


def get_response_paths(output_src, output_trgt, output_manual_src, output_manual_trgt, output_nomatch):
    output_src = alignmentutils.upload_file_binary(output_src)
    output_trgt = alignmentutils.upload_file_binary(output_trgt)
    output_manual_src = alignmentutils.upload_file_binary(output_manual_src)
    output_manual_trgt = alignmentutils.upload_file_binary(output_manual_trgt)
    output_nomatch = alignmentutils.upload_file_binary(output_nomatch)
    output_dict = {"source": output_src, "target": output_trgt, "manual_src": output_manual_src,
                   "manual_trgt": output_manual_trgt, "nomatch": output_nomatch}
    return output_dict


def build_final_response(source, target, output, object_in):
    result = {"status": "COMPLETED",
              "jobID": object_in["jobID"],
              "startTime": object_in["startTime"],
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


if __name__ == '__main__':
    log.info("Consumer running.......")
    process()
