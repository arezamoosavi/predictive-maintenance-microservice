import os
import uuid
import json
import eventlet
from datetime import datetime
from eventlet.event import Event
from nameko.rpc import rpc
from nameko.extensions import DependencyProvider

import happybase


def get_hbase_table(table_name):
    connection = happybase.Connection(host="hbase", port=9090, autoconnect=True)
    table = connection.table(table_name)
    return table


def save_to_hbase(data):
    table = get_hbase_table("nasa-data")
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    date_row = now.isoformat()
    dict_data = json.loads(data)

    print(data, type(data))
    with table.batch(timestamp=int(timestamp), transaction=True) as batch:
        batch.put(
            date_row,
            {
                "s:data": " ".join(str(e) for e in dict_data["data"]),
                "s:life_cycle": str(dict_data["life_cycle"]),
                "s:task_id": str(dict_data["task_id"]),
            },
        )

    return True


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
