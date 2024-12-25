from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import requests
from pydantic import BaseModel
import models
from schemas import SaveExtractedDataRequest
from database import Base, SessionLocal, engine

app = FastAPI()

class FileData(BaseModel):
    file: str
    file_name: str
    document_type_name: str = "metadata-invoice"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.post("/extract-data/")
async def process_document(file_data: FileData):
    payload = {
        "file": file_data.file,
        "file_name": file_data.file_name,
        "document_type_name": "simple-invoice"
    }

    url = "https://developers.typless.com/api/extract-data"

    token = os.getenv("TYPLESS_API_TOKEN")
    if not token:
        raise HTTPException(status_code=500, detail="API token is not set")

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Token {token}"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        extracted_fields = response.json().get('extracted_fields', [])
        print(extracted_fields)
        return JSONResponse(content={"extracted_fields": extracted_fields})
    else:
        return JSONResponse(content={"error": "Failed to process the document."}, status_code=500)

@app.post("/save-extracted-data/")
async def save_extracted_data(request: SaveExtractedDataRequest, db: SessionLocal = Depends(get_db)):
    try:
        for field in request.extracted_fields:
            db.add(models.ExtractedField(
                name=field.name,
                value=field.value,
                confidence_score=field.confidence_score
            ))
        db.commit()
        return {"message": "Data saved successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save data: {str(e)}")