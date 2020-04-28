import json
import logging
import traceback

import os
import datetime as dt
from kafka import KafkaProducer

log = logging.getLogger('file')
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
        log.info("Pushing to the Kafka Queue......")
        try:
            log.info(object_in)
            producer.send(align_job_topic, value=object_in)
            producer.flush()
            log.info("Done.")
        except Exception as e:
            log.error("Exception while producing: " + str(e))
            log.error(str(traceback.print_exc()))
