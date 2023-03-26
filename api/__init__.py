import os

from fastapi import FastAPI
survey_api = FastAPI()
from fastapi import responses

from typing import Annotated

import httpx
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse,FileResponse



import models


import requests




@survey_api.post("/uploadfile")
async def create_upload_file(file: UploadFile):
    content = await file.read()
    obj = models.CxmFormat(content.decode())
    #path=os.getcwd()+"/model.3dm"
    #obj.dump3dm().Write(path,7)
    obj.commit()
    return "Ok"


@survey_api.get("/")
async def main():
    content = """

<body>
</form>
<form action="/cxm/api/v2/survey/uploadfile/" enctype="multipart/form-data" method="post">
<input name="file" type="file">
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)

