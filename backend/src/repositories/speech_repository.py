import uuid
from typing import Optional, List
from sqlmodel import Session, select
from models import SpeechRecord # Adjusted import

class SpeechRepository:
    def create(
        self, db: Session, *, text: str, audio_file_name: str
    ) -> SpeechRecord:
        """Create a new speech record with a unique ID."""
        record_id = str(uuid.uuid4())
        # audio_file_name should be just the name of the file, e.g., <uuid>.wav
        db_record = SpeechRecord(id=record_id, text=text, audio_file=audio_file_name)
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record

    def get_by_id(self, db: Session, record_id: str) -> Optional[SpeechRecord]:
        """Get a speech record by ID."""
        return db.get(SpeechRecord, record_id)

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[SpeechRecord]:
        """Get multiple speech records with pagination."""
        return db.exec(
            select(SpeechRecord)
            .offset(skip)
            .limit(limit)
            .order_by(SpeechRecord.created_at.desc())
        ).all()

    def get_by_text_search(
        self, db: Session, *, search_text: str, skip: int = 0, limit: int = 100
    ) -> List[SpeechRecord]:
        """Search speech records by text content."""
        return db.exec(
            select(SpeechRecord)
            .where(SpeechRecord.text.contains(search_text))
            .offset(skip)
            .limit(limit)
            .order_by(SpeechRecord.created_at.desc())
        ).all()

    def delete(self, db: Session, *, record_id: str) -> Optional[SpeechRecord]:
        """Delete a speech record."""
        record: Optional[SpeechRecord] = db.get(SpeechRecord, record_id)
        if record:
            db.delete(record)
            db.commit()
        return record

    def update_text(
        self, db: Session, *, record_id: str, new_text: str
    ) -> Optional[SpeechRecord]:
        """Update the text of a speech record."""
        record: Optional[SpeechRecord] = db.get(SpeechRecord, record_id)
        if record:
            record.text = new_text
            db.add(record)
            db.commit()
            db.refresh(record)
        return record 