import os
import json

from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel, conlist
from nameko.standalone.rpc import ServiceRpcProxy


def rpc_proxy(job):
    # the ServiceRpcProxy instance isn't thread safe so we constuct one for
    # each request; a more intelligent solution would be a thread-local or
    # pool of shared proxies
    config = {"AMQP_URI": os.getenv("RMQ")}
    return ServiceRpcProxy(job, config)


app = FastAPI()


@app.get("/")
async def health_check():
    return {"Hello": "World"}


class DataModel(BaseModel):
    data: conlist(float, min_items=15, max_items=15)


@app.post("/pred/")
async def predict(sent_data: DataModel):
    try:
        with rpc_proxy("mltask") as task_proxy:
            prediction = task_proxy.get_predict(sent_data.data)
        return {"messege": "Successfully Done!", "response": json.loads(prediction)}
    except Exception as e:
        print("EXECPTION: ", e)
        return {"messege": e, "response": "Error!"}


@app.get("/dataset/")
async def all_data():
    try:
        with rpc_proxy("dbtask") as task_proxy:
            query_results = task_proxy.get_all_data("nasa-data")
        return {"messege": "Successfully Done!", "response": json.loads(query_results)}
    except Exception as e:
        print("EXECPTION: ", e)
        return {"messege": e, "response": "Error!"}
