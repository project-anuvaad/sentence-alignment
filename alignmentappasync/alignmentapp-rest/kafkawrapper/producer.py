from json import dumps

from kafka import KafkaProducer
import os
import datetime as dt
#from .consumer import Consumer

cluster_details = os.environ.get('KAFKA_CLUSTER_DETAILS', 'localhost:9092')
align_job_topic = os.environ.get('ALIGN_JOB_TOPIC', 'laser-align-job-register')
align_job_topic_partitions = os.environ.get('ALIGN_JOB_TOPIC_PARTITIONS',  2)


class Producer:

    def __init__(self):
        pass

    def instantiate(self):
        producer = KafkaProducer(bootstrap_servers = [cluster_details],
                                 api_version=(0,11,5),
                                 value_serializer=lambda x: dumps(x).encode('utf-8'))
        return producer

    def push_to_queue(self, object_in):
        producer = self.instantiate()
        print(str(dt.datetime.now()) + " : Pushing to the Kafka Queue......")
        print(object_in)
        producer.send(align_job_topic, object_in)
        producer.flush()