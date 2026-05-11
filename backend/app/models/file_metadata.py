from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.core.database import Base

class FileMetadata(Base):
    __tablename__ = "file_metadata"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True, nullable=False)
    file_type = Column(String, nullable=False) # e.g., 'pdf', 'mp3', 'mp4'
    upload_date = Column(DateTime, default=datetime.utcnow)
    extracted_text = Column(Text, nullable=True) # Full text or summary
