"""
Note:
Notice the 'async:true' specifier below. This ensures the associated run,
debug, and profile commands run this script on a non-ui thread so Rhino
UI does not get locked when script is running.
"""

# ! async:true

from __future__ import absolute_import, annotations
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


class CxmGeodesyService(RpycService, configs=CONFIGS):
    ...


class ServiceController:
    def __init__(self, server):
        super().__init__()
        self.server = server

    def __call__(self, host, port, **kwargs):
        self.server.host = host
        self.server.port = port
        for k, v in kwargs:
            self.server.__setattr__(k, v)



if __name__ == "__main__":
    import sys

    print(CONFIGS)
    pprint.pprint(os.environ)
    pprint.pprint(CxmGeodesyService.__dict__)
    sys.exit(CxmGeodesyService.run())
