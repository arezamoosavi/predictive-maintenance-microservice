import uuid
import json
import eventlet
from eventlet.event import Event
from nameko.rpc import rpc, RpcProxy
from nameko.extensions import DependencyProvider

from joblib import load

clf = load("forest_model.joblib")


def randomforest(data):
    result = clf.predict([data])
    eventlet.sleep()  # won't yield voluntarily since there's no i/o
    return result


class PredictLife(DependencyProvider):
    def predict(self, data):
        # generate unique id
        task_id = uuid.uuid4().hex

        # execute it in a container thread and send the result to an Event
        event = Event()
        gt = self.container.spawn_managed_thread(lambda: randomforest(data))
        gt.link(lambda res: event.send(res.wait()))

        while True:
            if event.ready():
                life_cycle = event.wait()
                retJson = {
                    "data": data,
                    "life_cycle": life_cycle[0],
                    "task_id": task_id,
                }

                return json.dumps(retJson)
            eventlet.sleep()

    def get_dependency(self, worker_ctx):
        class MLApi(object):
            predict = self.predict

        return MLApi()


class MLService(object):
    name = "mltask"

    # dash_rpc = RpcProxy("dashtask")
    db_rpc = RpcProxy("dbtask")

    processor = PredictLife()

    @rpc
    def get_predict(self, data):
        result = self.processor.predict(data)

        # self.dash_rpc.send_the_data_to_kafka(result)
        self.db_rpc.save_the_data_to_hbase(result)

        return result
