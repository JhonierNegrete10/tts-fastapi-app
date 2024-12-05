from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
from pydantic import BaseModel

class TextInput(BaseModel):
    text: str

def utcnow():
    return datetime.now(timezone.utc)

class SpeechRecord(SQLModel, table=True):
    id: str = Field(primary_key=True)
    text: str = Field(index=True)
    audio_file: str
    created_at: datetime = Field(default_factory=utcnow)