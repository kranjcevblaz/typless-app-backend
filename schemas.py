from pydantic import BaseModel
from typing import List

class ExtractedFieldData(BaseModel):
    name: str
    value: str
    confidence_score: float

class SaveExtractedDataRequest(BaseModel):
    extracted_fields: List[ExtractedFieldData]