"""
Note:
Notice the 'async:true' specifier below. This ensures the associated run,
debug, and profile commands run this script on a non-ui thread so Rhino
UI does not get locked when script is running.
"""

# ! async:true

from __future__ import absolute_import, annotations

import threading

import models
from mmcore.addons.rhino import rhino3dm
import os
import dotenv

dotenv.load_dotenv("/mmcore/.env")
CONFIGS = os.getenv("CONFIGS_URL")
os.environ["RPYC_CONFIGS"] = CONFIGS
import pprint
from mmcore.services.service import RpycService
import sys
from mmcore.services.client import get_connection_by_host_port

# http://storage.yandexcloud.net/box.contextmachine.space/share/configs/configs.yaml



import uvicorn
from fastapi.background import BackgroundTasks

from fastapi import APIRouter

from fastapi import FastAPI
class CxmServiceApi(APIRouter):
    ...


app = FastAPI()



class CxmGeodesyService(RpycService, configs=CONFIGS):
    ...
from fastapi import responses

from typing import Annotated

import httpx
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse






import requests






@app.post("/uploadfile")
async def create_upload_file(file: UploadFile):
    content = await file.read()
    obj = models.CxmFormat(content.decode())

    obj.commit()

    return "OK"


@app.get("/")
async def main():
    content = """

<body>
</form>
<form action="/uploadfile/" enctype="multipart/form-data" method="post">
<input name="file" type="file">
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)


class ServiceController:
    @property
    def cxmapi(self):
        return app

    def __init__(self, server, host, port, **kwargs):
        super().__init__()
        self.server = server
        self.server.host = host
        self.server.port = port
        self.name = os.getenv("SERVICE_NAME")
        for k, v in kwargs:
            self.server.__setattr__(k, v)

        self.thread = threading.Thread(target=lambda: sys.exit(self.server.run()), name="survey-service")

    def __call__(self):
        try:
            sys.exit(self.server.run())
        except KeyboardInterrupt as err:
            print("stopping..")
            sys.exit(0)
        except Exception as err:
            raise err

    def run_thread(self):
        self.thread.start()


if __name__ == "__main__":
    print(CONFIGS)
    cntrl = ServiceController(CxmGeodesyService, host="0.0.0.0", port=4777)
    cntrl.run_thread()
    print(
        "services running at:"
        "*:4777 - rpyc"
        "*5777 - uvicorn"
    )
    uvicorn.run("main:app", host="0.0.0.0", port=5777)
