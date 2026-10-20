from datetime import datetime
from pydantic import BaseModel
from sqlmodel import Field


class TextInput(BaseModel):
    text: str = Field(..., description="The text to be synthesized.")


class SpeechRecord(BaseModel):
    id: str = Field(..., description="The unique identifier for the speech record.")
    audio_file: str = Field(..., description="The audio file to be synthesized.")
    created_at: datetime = Field(
        ..., description="The date and time the speech record was created."
    )



class SpeechRecordOutput(SpeechRecord):
    text: str = Field(..., description="The text to be synthesized.")
