from typing import Optional, List
from sqlmodel import Session, select
from models import SpeechRecord


class CRUDBase:
    def __init__(self, model):
        self.model: SpeechRecord = model


class CRUDSpeechRecord(CRUDBase):
    def __init__(self):
        super().__init__(SpeechRecord)

    def create(
        self, db: Session, *, record_id: str, text: str, audio_file: str
    ) -> SpeechRecord:
        """Create a new speech record."""
        db_record = SpeechRecord(id=record_id, text=text, audio_file=audio_file)
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record

    def get_by_id(self, db: Session, record_id: str) -> Optional[SpeechRecord]:
        """Get a speech record by ID."""
        return db.get(self.model, record_id)

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[SpeechRecord]:
        """Get multiple speech records with pagination."""
        return db.exec(
            select(self.model)
            .offset(skip)
            .limit(limit)
            .order_by(self.model.created_at.desc())
        ).all()

    def get_by_text_search(
        self, db: Session, *, search_text: str, skip: int = 0, limit: int = 100
    ) -> List[SpeechRecord]:
        """Search speech records by text content."""
        return db.exec(
            select(self.model)
            .where(self.model.text.contains(search_text))
            .offset(skip)
            .limit(limit)
            .order_by(self.model.created_at.desc())
        ).all()

    def delete(self, db: Session, *, record_id: str) -> Optional[SpeechRecord]:
        """Delete a speech record."""
        record: SpeechRecord = db.get(self.model, record_id)
        if record:
            db.delete(record)
            db.commit()
        return record

    def update_text(
        self, db: Session, *, record_id: str, new_text: str
    ) -> Optional[SpeechRecord]:
        """Update the text of a speech record."""
        record: SpeechRecord = db.get(self.model, record_id)
        if record:
            record.text = new_text
            db.add(record)
            db.commit()
            db.refresh(record)
        return record


# Create a CRUD instance
speech_records = CRUDSpeechRecord()
