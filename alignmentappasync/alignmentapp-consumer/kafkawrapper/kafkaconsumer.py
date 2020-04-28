import json
import logging
import traceback

from kafka import KafkaConsumer
import os

log = logging.getLogger('file')
cluster_details = os.environ.get('KAFKA_CLUSTER_DETAILS', 'localhost:9092')
align_job_topic = "laser-align"
#align_job_topic = os.environ.get('ALIGN_JOB_TOPIC', 'laser-align-job-register')
align_job_consumer_grp = os.environ.get('ALIGN_JOB_CONSUMER_GRP', 'laser-align-job-consumer-group')


class Consumer:

    def __init__(self):
        pass

    def get_consumer(self):
        consumer = KafkaConsumer(align_job_topic,
                             bootstrap_servers=[cluster_details],
                             api_version=(1, 0, 0),
                             group_id=align_job_consumer_grp,
                             auto_offset_reset='earliest',
                             enable_auto_commit=True,
                             max_poll_records=1,
                             value_deserializer=lambda x: self.handle_json(x))
        return consumer

    def handle_json(self, x):
        try:
            return json.loads(x.decode('utf-8'))
        except Exception as e:
            log.error("Exception while deserialising: " + str(e))
            log.error(str(traceback.print_exc()))
        return {}
