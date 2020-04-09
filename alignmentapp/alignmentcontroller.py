#!/bin/python
from flask import Flask, jsonify, request
from alignmentapp.alignmentservice import AlignmentService

app = Flask(__name__)

@app.route('/sentence-alignment/files/align', methods = ["POST"])
def alignsentences():
    service = AlignmentService()
    data = request.get_json()
    error = service.validate_input(data)
    if error is not None:
        return error
    source_file = data["source"]["filepath"]
    target_file = data["target"]["filepath"]
    response = service.process(source_file, target_file)
    print("Aligned Successfully ("+source_file +" | "+target_file+")")
    return response

if __name__ == '__main__':
   app.run()