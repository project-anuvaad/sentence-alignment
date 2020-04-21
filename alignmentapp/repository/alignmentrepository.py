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

    def create_job(self, object):
        col = self.instantiate()
        id = col.insert_one(object)
        print("Inserted at: ", id)

    def update_job(self, object, job_id):
        col = self.instantiate()
        query = {"jobID" : job_id}
        new = {"$set": object}
        col.update_one(query, new)
        print("Updated!")

    def search_job(self, job_id):
        col = self.instantiate()
        query = {"jobID" : job_id}
        result = col.find(query)
        return result