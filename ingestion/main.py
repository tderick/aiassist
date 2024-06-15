from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from enum import Enum
import uvicorn

from dataingestion.ingestion import WebPageIngestion

app = FastAPI()

class InputType(str, Enum):
    sitemap = "sitemap"
    pdf = "pdf"

@app.post("/api/v1/dataingestion/url/")
async def url_data_ingestion(page_url: str = Form(...), bot_id: str = Form(...)):
    WebPageIngestion(url=page_url, bot_id=bot_id).ingest()
    return {"status": "success"}
  


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)




# @app.post("/api/v1/dataingestion/url/")
# async def url_data_ingestion(input_type: InputType = Form(...), file: UploadFile = File(...)):
#     if input_type == InputType.xml:
#         if file.content_type != "application/xml" and not file.filename.endswith(".xml"):
#             raise HTTPException(status_code=400, detail="Invalid file type. Expected an XML file.")
#         content = await file.read()
#         # Process the XML file here
#         return {"filename": file.filename, "content_type": file.content_type, "input_type": input_type}

#     elif input_type == InputType.pdf:
#         if file.content_type != "application/pdf" and not file.filename.endswith(".pdf"):
#             raise HTTPException(status_code=400, detail="Invalid file type. Expected a PDF file.")
#         content = await file.read()
#         # Process the PDF file here
#         return {"filename": file.filename, "content_type": file.content_type, "input_type": input_type}

#     else:
#         raise HTTPException(status_code=400, detail="Invalid input type. Expected 'xml' or 'pdf'.")
