import json
import traceback
from json import dumps

from kafka import KafkaProducer
import os
import datetime as dt
import time

cluster_details = os.environ.get('KAFKA_CLUSTER_DETAILS', 'localhost:9095')
align_job_topic = os.environ.get('ALIGN_JOB_TOPIC', 'laser-align-job-register')
align_job_topic_partitions = os.environ.get('ALIGN_JOB_TOPIC_PARTITIONS', 2)


class Producer:

    def __init__(self):
        pass

    def instantiate(self):
        producer = KafkaProducer(bootstrap_servers=[cluster_details],
                                 api_version=(1, 0, 0),
                                 value_serializer=lambda x: json.dumps(x).encode('utf-8'))
        return producer

    def push_to_queue(self, object_in):
        producer = self.instantiate()
        print(str(dt.datetime.now()) + " : Pushing to the Kafka Queue......")
        try:
            print(object_in)
            producer.send(align_job_topic, value=object_in)
            producer.flush()
            print(str(dt.datetime.now()) + " : Done.")
        except Exception as e:
            print("Exception while producing: " + str(e))
            traceback.print_exc()
