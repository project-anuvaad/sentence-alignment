from kafka import KafkaProducer
import os

cluster_details = os.environ.get('KAFKA_CLUSTER_DETAILS', 'localhost:1234')
align_job_topic = os.environ.get('ALIGN_JOB_TOPIC', 'laser-align-job-register')
align_job_topic_partitions = os.environ.get('ALIGN_JOB_TOPIC_PARTITIONS',  2)


class Producer:

    def __init__(self):
        pass

    def instantiate(self):
        producer = KafkaProducer(bootstrap_servers = cluster_details)
        return producer

    def push_to_queue(self, object):
        producer = self.instantiate()
        producer.send(align_job_topic, object)

