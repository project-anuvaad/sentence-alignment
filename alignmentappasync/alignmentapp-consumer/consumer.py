import json
from json import loads

from kafka import KafkaConsumer
import os
import datetime as dt
from service.alignmentservice import AlignmentService

cluster_details = os.environ.get('KAFKA_CLUSTER_DETAILS', 'localhost:9092')
align_job_topic = os.environ.get('ALIGN_JOB_TOPIC', 'laser-align-job-register')
align_job_consumer_grp = os.environ.get('ALIGN_JOB_CONSUMER_GRP', 'laser-align-job-consumer-group')


def instantiate():
    consumer = KafkaConsumer(align_job_topic,
                             bootstrap_servers=[cluster_details],
                             group_id=align_job_consumer_grp,
                             api_version=(1, 0, 0),
                             auto_offset_reset='earliest',
                             enable_auto_commit=True,
                             value_deserializer=lambda x: handle_json(x))
    consumer.poll(10)
    return consumer


def consume():
    consumer = instantiate()
    print(str(dt.datetime.now()) + " : Consuming from the Kafka Queue......")
    service = AlignmentService()
    for msg in consumer:
        print(msg)
        data = msg.value
        service.process(data)


def handle_json(x):
    try:
        return json.loads(x.decode('utf-8'))
    except Exception as e:
        print("Exception: ", e)
        return {}


consume()
