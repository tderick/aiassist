from fastapi import FastAPI,Form
import uvicorn

from dataingestion.ingestion import WebPageIngestion

app = FastAPI()


@app.post("/api/v1/dataingestion/url/")
async def url_data_ingestion(page_url: str = Form(...), bot_id: str = Form(...)):
    WebPageIngestion(url=page_url, bot_id=bot_id).ingest()
    return {"status": "success"}
  


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

