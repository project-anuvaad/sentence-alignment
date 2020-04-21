from kafka import KafkaConsumer
import os
from service.alignmentservice import AlignmentService

cluster_details = os.environ.get('KAFKA_CLUSTER_DETAILS', 'localhost:1234')
align_job_topic = os.environ.get('ALIGN_JOB_TOPIC', 'laser-align-job-register')
align_job_topic_partitions = os.environ.get('ALIGN_JOB_TOPIC_PARTITIONS',  2)
align_job_consumer_grp = os.environ.get('ALIGN_JOB_CONSUMER_GRP', 'laser-align-job-consumer-group')


class Consumer:

    def __init__(self):
        pass

    def instantiate(self):
        consumer = KafkaConsumer(align_job_topic,
                                 bootstrap_servers = cluster_details,
                                 group_id = align_job_consumer_grp)
        return consumer

    def consume(self):
        service = AlignmentService()
        consumer = self.instantiate()
        for msg in consumer:
            data = msg.value
            service.process(data)


