import uuid
import json
import eventlet
from eventlet.event import Event
from nameko.rpc import rpc, RpcProxy
from nameko.extensions import DependencyProvider
from kafka import KafkaProducer

kafka_server = "kafka:9092"
producer = KafkaProducer(
    bootstrap_servers=[kafka_server],
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)

topic_name = "nasa-sensor-data"

list_of_sensors = [
    "Sensor_1",
    "Sensor_2",
    "Sensor_3",
    "Sensor_6",
    "Sensor_7",
    "Sensor_8",
    "Sensor_10",
    "Sensor_11",
    "Sensor_12",
    "Sensor_13",
    "Sensor_14",
    "Sensor_16",
    "Sensor_19",
    "Sensor_20",
    "Sensor_21",
]


def process_data(data):
    dict_data = json.loads(data)
    sensor_data = dict_data["data"]
    result_dict = dict(zip(list_of_sensors, sensor_data))
    result_dict["pred_life_cycle"] = dict_data["life_cycle"]
    return result_dict


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

        pr_data = process_data(data)
        event = Event()
        gt = self.container.spawn_managed_thread(lambda: send_to_kafka(pr_data))
        gt.link(lambda res: event.send(res.wait()))
        eventlet.sleep()

        while True:
            if event.ready():
                is_sent = event.wait()
                return is_sent
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
