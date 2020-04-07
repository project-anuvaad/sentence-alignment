#!/bin/python
from flask import Flask, jsonify, request
from alignmentapp.alignmentservice import AlignmentService

app = Flask(__name__)

@app.route('/align/files', methods = ["POST"])
def print():
    service = AlignmentService()
    data = request.get_json()
    if None == data["source"]:
        get_error("SOURCE_NOT_FOUND", "Details of the source not available")
    if None == data["target"]:
        get_error("TARGET_NOT_FOUND", "Details of the target not available")
    source_file = data["source"]["filepath"]
    target_file = data["target"]["filepath"]
    response = service.process(source_file, target_file)
    return response


def get_error(code, message):
    return jsonify({"status": "ERROR", "code": code, "message": message})

if __name__ == '__main__':
   app.run()