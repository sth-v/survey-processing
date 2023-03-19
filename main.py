"""
Note:
Notice the 'async:true' specifier below. This ensures the associated run,
debug, and profile commands run this script on a non-ui thread so Rhino
UI does not get locked when script is running.
"""

#! async:true

from __future__ import absolute_import, annotations
from mmcore.services.service import RpycService
import sys


class MyService(RpycService, configs='http://storage.yandexcloud.net/box.contextmachine.space/share/configs/configs.yaml'):
    ...
if __name__ == "__main__":
    sys.exit(MyService.run())
