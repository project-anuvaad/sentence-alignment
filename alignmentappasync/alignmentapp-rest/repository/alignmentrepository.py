#!/bin/python
import binascii
import codecs
import json
import os
import pymongo

import requests
import numpy as np
import csv
import time

mongo_client = os.environ.get('MONGO_CLIENT', 'mongodb://localhost:27017/')
mongo_alignment_db = os.environ.get('MONGO_ALIGNMENT_DB', 'anuvaad-laser-alignment')
mongo_alignment_col = os.environ.get('MONGO_ALIGNMENT_COL', 'alignment-job')

class AlignmentRepository:

    def __init__(self):
        pass

    def instantiate(self):
        client = pymongo.MongoClient(mongo_client)
        db = client[mongo_alignment_db]
        col = db[mongo_alignment_col]
        return col

    def create_job(self, object_in):
        col = self.instantiate()
        col.insert_one(object_in)

    def update_job(self, object_in, job_id):
        col = self.instantiate()
        query = {"jobID" : job_id}
        new = {"$set": object_in}
        col.update_one(query, new)

    def search_job(self, job_id):
        col = self.instantiate()
        query = {"jobID" : job_id}
        res = col.find(query, {'_id': False})
        result = []
        for record in res:
            print(record)
            result.append(record)
        return result