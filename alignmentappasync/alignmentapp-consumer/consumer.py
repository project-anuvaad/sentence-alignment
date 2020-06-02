import json
import logging
import traceback

from kafka import KafkaConsumer
import os
from service.alignmentservice import AlignmentService
from utilities.alignmentutils import AlignmentUtils
from logging.config import dictConfig


log = logging.getLogger('file')
cluster_details = os.environ.get('KAFKA_CLUSTER_DETAILS', 'localhost:9092')
consumer_poll_interval = os.environ.get('CONSUMER_POLL_INTERVAL', 10)
align_job_topic = "laser-align-job-register-b"
#align_job_topic = os.environ.get('ALIGN_JOB_TOPIC', 'laser-align-job-register')
anu_dp_wf_aligner_in_topic = os.environ.get('ANU_DP_WF_ALIGNER_IN_TOPIC', 'anuvaad-dp-tools-aligner-input')
align_job_consumer_grp = os.environ.get('ALIGN_JOB_CONSUMER_GRP', 'laser-align-job-consumer-group')

# Method to instantiate the kafka consumer
def instantiate():
    consumer = KafkaConsumer(align_job_topic,
                             bootstrap_servers=[cluster_details],
                             api_version=(1, 0, 0),
                             group_id=align_job_consumer_grp,
                             auto_offset_reset='earliest',
                             enable_auto_commit=True,
                             max_poll_records=1,
                             value_deserializer=lambda x: handle_json(x))
    consumer.poll(consumer_poll_interval)
    return consumer

# Method to read and process the requests from the kafka queue
def consume():
    consumer = instantiate()
    service = AlignmentService()
    log.info("Consumer running.......")
    try:
        data = {}
        topic = None
        for msg in consumer:
            log.info("Consuming from the Kafka Queue......")
            data = msg.value
            topic = msg.topic
            break
        if topic is anu_dp_wf_aligner_in_topic:
            util = AlignmentUtils()
            data["taskID"] = util.generate_task_id()
            service.process(data, True)
        else:
            service.process(data, False)
    except Exception as e:
        log.error("Exception while consuming: " + str(e))
        traceback.print_exc()
    finally:
        consumer.close()

# Method that provides a deserialiser for the kafka record.
def handle_json(x):
    try:
        return json.loads(x.decode('utf-8'))
    except Exception as e:
        log.error("Exception while deserialising: " + str(e))
        traceback.print_exc()
        return {}

# Log config
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] {%(filename)s:%(lineno)d} %(threadName)s %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {
        'info': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'filename': 'info.log'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'stream': 'ext://sys.stdout',
        }
    },
    'loggers': {
        'file': {
            'level': 'DEBUG',
            'handlers': ['info', 'console'],
            'propagate': ''
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['info', 'console']
    }
})


if __name__ == '__main__':
    while True:
        consume()