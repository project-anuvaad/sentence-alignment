#!/bin/python
import logging
import os

from flask import Flask, jsonify, request
import datetime as dt
from service.alignmentservice import AlignmentService
from utilities.alignmentutils import AlignmentUtils
from logging.config import dictConfig

app = Flask(__name__)
context_path = os.environ.get('SA_CONTEXT_PATH', '/sentence-alignment')


@app.route(context_path + '/alignment/align/async', methods=["POST"])
def createalignmentjob():
    service = AlignmentService()
    util = AlignmentUtils()
    data = request.get_json()
    error = service.validate_input(data)
    if error is not None:
        return error
    source_file = data["source"]["filepath"]
    target_file = data["target"]["filepath"]
    job_id = util.generate_job_id()
    response = {"source": source_file, "target": target_file, "jobID": job_id, "status": "START"}
    service.register_job(response)
    return response

@app.route(context_path + '/alignment/jobs/get/<job_id>', methods=["GET"])
def searchjobs(job_id):
    service = AlignmentService()
    response = service.search_jobs(job_id)
    return jsonify(response)

@app.route('/health', methods=["GET"])
def health():
    response = {"code": "200", "status": "ACTIVE"}
    return jsonify(response)


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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
