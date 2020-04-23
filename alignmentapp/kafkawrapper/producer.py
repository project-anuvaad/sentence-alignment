import json
from json import dumps

from kafka import KafkaProducer
import os
import datetime as dt
import time

cluster_details = os.environ.get('KAFKA_CLUSTER_DETAILS', 'localhost:9092')
align_job_topic_partitions = os.environ.get('ALIGN_JOB_TOPIC_PARTITIONS', 2)


class Producer:

    def __init__(self):
        pass

    def get_producer(self):
        producer = KafkaProducer(bootstrap_servers=[cluster_details],
                                 api_version=(1, 0, 0),
                                 value_serializer=lambda x: json.dumps(x).encode('utf-8'))
        return producer
