# from lxml import etree

import os
import shutil

from typing import Annotated
from fastapi import FastAPI,Form, File, UploadFile, HTTPException
import uvicorn

from dataingestion.ingestion import WebPageIngestion, FileIngestion
from dataretrieval.retriever import DataRetrieval

app = FastAPI()

# Configuring upload folder
UPLOAD_FOLDER = 'uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/api/v1/dataingestion/url/")
async def url_data_ingestion(page_url: str = Form(...), bot_id: str = Form(...)):
    WebPageIngestion(url=page_url, bot_id=bot_id).ingest()
    return {"status": "success"}

@app.post("/api/v1/dataingestion/file/")
async def file_data_ingestion(file: UploadFile = File(...), bot_id: str = Form(...)):

    uniquefolder = file.filename.replace(" ", "").replace(".", "").replace("(", "").replace(")", "")
    os.makedirs(os.path.join(UPLOAD_FOLDER, uniquefolder), exist_ok=True)

    file_location = os.path.join(UPLOAD_FOLDER, uniquefolder, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    FileIngestion(dir=os.path.join(UPLOAD_FOLDER,uniquefolder), bot_id=bot_id).ingest()

    shutil.rmtree(UPLOAD_FOLDER+uniquefolder)
    return {"status": "success"}

# @app.post("/api/v1/dataingestion/sitemap/")
# async def sitemap_data_ingestion(sitemap: Annotated[bytes, File()], bot_id: str = Form(...)):
#     xml_dict = {}
#     try:
#         root = etree.fromstring(sitemap.file.read().decode('utf-8'))
#         for child in root.getchildren():
#             xml_dict[child.tag] = child.text
        
#         import pdb;pdb.set_trace()

#     except etree.XMLSyntaxError as e:
#         raise HTTPException(status_code=400, detail="Invalid XML file")
    
    
#     return {"status": "success"}
  

@app.post("/api/v1/retriever/")
async def url_data_ingestion(question: str=Form(...),bot_id: str = Form(...)):
    response = DataRetrieval(question=question, bot_id=bot_id).retrieve()
    return {"data": response}
  


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

