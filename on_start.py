
from __future__ import absolute_import, annotations

import os
import subprocess
import sys


def install(python=None):
    if python is None:
        python=sys.executable
    proc = subprocess.Popen(f"{python} -m pip install -r {os.getcwd()}/req.txt".split(" "))
    proc.wait()
    proc2 = subprocess.Popen(
        f"{python} -m pip install --force-reinstall git+https://github.com/sth-v/cxm_boto_client.git".split(" "))
    proc2.wait()
    proc3 = subprocess.Popen(
        f"{python} -m pip install --force-reinstall git+https://github.com/contextmachine/cxmdata.git".split(" "))
    proc3.wait()


if __name__ == "__main__":
    install(sys.argv[1])
