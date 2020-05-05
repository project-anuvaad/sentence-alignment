#!/bin/python
import os
import pymongo

mongo_client = os.environ.get('MONGO_CLIENT', 'mongodb://localhost:27017/')
mongo_alignment_db = os.environ.get('MONGO_ALIGNMENT_DB', 'anuvaad-laser-alignment')
mongo_alignment_col = os.environ.get('MONGO_ALIGNMENT_COL', 'alignment-job')

class AlignmentRepository:

    def __init__(self):
        pass

    # Initialises and fetches mongo client
    def instantiate(self):
        client = pymongo.MongoClient(mongo_client)
        db = client[mongo_alignment_db]
        col = db[mongo_alignment_col]
        return col

    # Updates the object in the mongo collection
    def update_job(self, object_in, job_id):
        col = self.instantiate()
        col.replace_one(
            {"jobID" : job_id},
            object_in
        )