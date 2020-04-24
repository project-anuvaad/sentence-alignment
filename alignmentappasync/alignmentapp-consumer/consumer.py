import json
import traceback

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
                             api_version=(1, 0, 0),
                             group_id=align_job_consumer_grp,
                             auto_offset_reset='earliest',
                             enable_auto_commit=True,
                             value_deserializer=lambda x: handle_json(x))
    return consumer


def consume():
    consumer = instantiate()
    service = AlignmentService()
    print(str(dt.datetime.now()) + " : Consumer running.......")
    try:
        for msg in consumer:
            print(str(dt.datetime.now()) + " : Consuming from the Kafka Queue......")
            data = msg.value
            service.process(data)
    except KeyboardInterrupt:
        sys.exit()
    except Exception as e:
        print(str(dt.datetime.now()) + " : Exception while consuming: " + str(e))
        traceback.print_exc()

def handle_json(x):
    try:
        return json.loads(x.decode('utf-8'))
    except Exception as e:
        print(str(dt.datetime.now()) + " : Exception while deserialising: " + str(e))
        traceback.print_exc()
        return {}


if __name__ == '__main__':
    while True:
        consume()
