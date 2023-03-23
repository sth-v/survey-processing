"""
Note:
Notice the 'async:true' specifier below. This ensures the associated run,
debug, and profile commands run this script on a non-ui thread so Rhino
UI does not get locked when script is running.
"""

# ! async:true

from __future__ import absolute_import, annotations

import threading

from mmcore.addons.rhino import rhino3dm
import os
import dotenv

dotenv.load_dotenv("/mmcore/.env")
import pprint
from mmcore.services.service import RpycService
import sys
from mmcore.services.client import get_connection_by_host_port

# http://storage.yandexcloud.net/box.contextmachine.space/share/configs/configs.yaml

CONFIGS = os.getenv("CONFIGS_URL")

import uvicorn
from fastapi.background import BackgroundTasks

from fastapi import APIRouter


class CxmServiceApi(APIRouter):
    ...


app = CxmServiceApi(prefix=os.getenv("SERVICE_NAME"), on_startup=[lambda: x])


class CxmGeodesyService(RpycService, configs=CONFIGS):
    ...


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
        self.thread = threading.Thread(target=self, name=self.name)

    def __call__(self):
        try:
            sys.exit(self.server.run())
        except KeyboardInterrupt as err:
            print("stopping..")
            sys.exit(0)
        except Exception as err:
            raise err


if __name__ == "__main__":
    print(CONFIGS)
    pprint.pprint(os.environ)
    pprint.pprint(CxmGeodesyService.__dict__)
    sys.exit(CxmGeodesyService.run())
