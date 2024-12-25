from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float
from database import Base

class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    value = Column(String)
    confidence_score = Column(Float)

class FileData(BaseModel):
    file: str
    file_name: str
    document_type_name: str = "metadata-invoice"