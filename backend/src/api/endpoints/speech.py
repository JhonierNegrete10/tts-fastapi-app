from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlmodel import Session

from schemas import TextInput, SpeechRecord, SpeechRecordOutput

from services.speech_service import SpeechService
from database import get_session

from tts_model.local_model import TTSLocalModel
from repositories.speech_repository import SpeechRepository


def get_speech_service() -> SpeechService:
    tts_model = TTSLocalModel()
    speech_repo = SpeechRepository()
    return SpeechService(tts_model=tts_model, speech_repo=speech_repo)


router = APIRouter()


@router.post("/synthesize/", response_model=SpeechRecord)
async def synthesize_speech_endpoint(
    text_input: TextInput,
    session: Session = Depends(get_session),
    service: SpeechService = Depends(get_speech_service),  # Placeholder dependency
):
    return service.synthesize_speech(text_input=text_input, db_session=session)


@router.post("/synthesize_paragraphs/", response_model=SpeechRecord)
async def synthesize_paragraphs_endpoint(
    text_input: TextInput,
    session: Session = Depends(get_session),
    service: SpeechService = Depends(get_speech_service),  # Placeholder dependency
):
    return service.synthesize_paragraphs(text_input=text_input, db_session=session)


@router.post("/synthesize_file/", response_model=SpeechRecord)
async def synthesize_file_endpoint(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    service: SpeechService = Depends(get_speech_service),  # Placeholder dependency
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file name provided.")
    return await service.synthesize_from_file(file=file, db_session=session)


@router.get("/records/", response_model=List[SpeechRecord])
async def get_records_endpoint(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    session: Session = Depends(get_session),
    service: SpeechService = Depends(get_speech_service),  # Placeholder dependency
):
    return service.get_records(
        db_session=session, skip=skip, limit=limit, search=search
    )


@router.delete("/records/{record_id}", response_model=SpeechRecordOutput)
async def delete_record_endpoint(
    record_id: str,
    session: Session = Depends(get_session),
    service: SpeechService = Depends(get_speech_service),  # Placeholder dependency
):
    record = service.delete_record(record_id=record_id, db_session=session)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.put("/records/{record_id}", response_model=SpeechRecordOutput)
async def update_record_endpoint(
    record_id: str,
    text_input: TextInput,
    session: Session = Depends(get_session),
    service: SpeechService = Depends(get_speech_service),  # Placeholder dependency
):
    record = service.update_record_text(
        record_id=record_id, text_input=text_input, db_session=session
    )
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.get("/records/{record_id}", response_model=SpeechRecordOutput)
async def get_by_id_endpoint(
    record_id: str,
    session: Session = Depends(get_session),
    service: SpeechService = Depends(get_speech_service),  # Placeholder dependency
):
    return await service.get_by_id(record_id=record_id, db_session=session)


@router.get("/audio/{record_id}", response_class=FileResponse)
async def get_audio_endpoint(
    record_id: str,
    session: Session = Depends(get_session),
    service: SpeechService = Depends(get_speech_service),  # Placeholder dependency
):
    record_db = await service.get_by_id(record_id=record_id, db_session=session)
    # return await service.get_audio(record_id=record_id, db_session=session)
    return FileResponse(path=f"/audio_output/{record_db.audio_file}")
