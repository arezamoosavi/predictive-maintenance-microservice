import uuid
import json
import eventlet
from eventlet.event import Event
from nameko.rpc import rpc, 
from nameko.extensions import DependencyProvider
from kafka import KafkaProducer
from json import dumps

kafka_server = "kafka:9092"  # TODO: added to .env
producer = KafkaProducer(
    bootstrap_servers=[kafka_server],
    value_serializer=lambda x: dumps(x).encode("utf-8"),
)

topic_name = "nasa-sensor-data"


def send_to_kafka(data):
    try:
        producer.send(topic_name, value=data)
        producer.flush()
        return True
    except Exception as e:
        print(e)
        return False


class ProduceKafka(DependencyProvider):
    def send_it(self, data):

        event = Event()
        gt = self.container.spawn_managed_thread(lambda: send_to_kafka(data))
        gt.link(lambda res: event.send(res.wait()))
        eventlet.sleep()

    def get_dependency(self, worker_ctx):
        class DASH(object):
            send_it = self.send_it

        return DASH()


class DASHService(object):
    name = "dashtask"

    processor = ProduceKafka()

    @rpc
    def send_the_data_to_kafka(self, data):
        return self.processor.send_it(data)
