#!/bin/python
from flask import Flask, jsonify, request
import datetime as dt
from service.alignmentservice import AlignmentService
from utilities.alignmentutils import AlignmentUtils

app = Flask(__name__)


@app.route('/sentence-alignment/files/align', methods=["POST"])
def alignsentences():
    service = AlignmentService()
    util = AlignmentUtils()
    data = request.get_json()
    error = service.validate_input(data)
    if error is not None:
        return error
    source_file = data["source"]["filepath"]
    target_file = data["target"]["filepath"]
    print(str(dt.datetime.now()) + " : Alignment process Started......")
    job_id = util.generate_job_id()
    obj = {"source": source_file, "target": target_file, "jobID": job_id, "status": "START"}
    response = {}
    try:
        service.register_job(obj)
        response = service.process(obj)
        print(str(dt.datetime.now()) + " : Aligned Successfully (" + source_file + " | " + target_file + ")")
    except Exception as e:
        print("An error has occured while aligning: ", e)

    return response


if __name__ == '__main__':
    app.run()
