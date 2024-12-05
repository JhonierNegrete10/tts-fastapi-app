from fastapi import FastAPI, Depends, HTTPException
import os
import uvicorn
from models import TextInput, SpeechRecord
from database import get_session, create_db_and_tables
from sqlmodel import Session
from crud import speech_records
from tts_model import tts_model
import logging
import boto3
from fastapi.responses import StreamingResponse
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
logger = logging.getLogger("uvicorn.info")

app = FastAPI()
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),

)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/synthesize/", response_model=SpeechRecord)
async def synthesize_speech(
    text_input: TextInput, session: Session = Depends(get_session)
):
    # Generate audio
    try:
        audio_s3_url = tts_model.synthetic_voice(text_input.text)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"error intentando sintetizar {str(e)}"
        )
        # audio_s3_url:: "https://{S3_BUCKET}.s3.amazonaws.com/{s3_full_path}"
        # get the filename from the url
    audio_id = audio_s3_url.split("/")[-1]

    # Create database record using CRUD
    try:
        db_record = speech_records.create(
            db=session,
            record_id=audio_id,
            text=text_input.text,
            audio_file=audio_s3_url,
        )

        return db_record
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"error intentando guardar en db {str(e)}"
        )


@app.get("/audio/{record_id}")
async def get_audio(record_id: str, session: Session = Depends(get_session)):
    record = speech_records.get_by_id(db=session, record_id=record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    try:
        # Get S3 URL from your database
        s3_url = record.audio_file  # Your database query here

        # Parse bucket and key from S3 URL
        bucket_name = s3_url.split("/")[2].split(".")[0]
        key = "/".join(s3_url.split("/")[3:])

        # Get object from S3
        file_obj = s3_client.get_object(Bucket=bucket_name, Key=key)

        # Return streaming response
        return StreamingResponse(
            file_obj["Body"].iter_chunks(),
            media_type="audio/wav",  # Adjust content type as needed
            headers={"Content-Disposition": f'attachment; filename="{key}"'},
        )
    except ClientError as e:
        raise HTTPException(status_code=404, detail=f"Audio file not found {e}")


@app.get("/records/", response_model=list[SpeechRecord])
async def get_records(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    session: Session = Depends(get_session),
):
    if search:
        records = speech_records.get_by_text_search(
            db=session, search_text=search, skip=skip, limit=limit
        )
    else:
        records = speech_records.get_multi(db=session, skip=skip, limit=limit)
    return records


@app.delete("/records/{record_id}", response_model=SpeechRecord)
async def delete_record(record_id: str, session: Session = Depends(get_session)):
    record = speech_records.delete(db=session, record_id=record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    # Delete associated audio file
    audio_path = f"/audio_output/{record.audio_file}"
    if os.path.exists(audio_path):
        os.remove(audio_path)

    return record


@app.put("/records/{record_id}", response_model=SpeechRecord)
async def update_record(
    record_id: str, text_input: TextInput, session: Session = Depends(get_session)
):
    record = speech_records.update_text(
        db=session, record_id=record_id, new_text=text_input.text
    )
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    return record


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8989, reload=True, reload_delay=2)
