#!/bin/python
import os

from flask import Flask, jsonify, request
import datetime as dt
from service.alignmentservice import AlignmentService
from utilities.alignmentutils import AlignmentUtils

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
