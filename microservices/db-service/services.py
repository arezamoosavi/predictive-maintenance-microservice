import uuid
import json
import eventlet
from eventlet.event import Event
from nameko.rpc import rpc
from nameko.extensions import DependencyProvider


def save_to_hbase(data):
    try:
        return True
    except Exception as e:
        print(e)
        return False


class SaveHbase(DependencyProvider):
    def save_to(self, data):

        event = Event()
        gt = self.container.spawn_managed_thread(lambda: save_to_hbase(data))
        gt.link(lambda res: event.send(res.wait()))

        while True:
            if event.ready():
                is_saved = event.wait()
                return is_saved
            eventlet.sleep()

    def get_dependency(self, worker_ctx):
        class DBApi(object):
            save_to = self.save_to

        return DBApi()


class DBService(object):
    name = "dbtask"

    processor = SaveHbase()

    @rpc
    def save_the_data_to_hbase(self, data):
        return self.processor.save_to(data)
