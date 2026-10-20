import os
import uuid
import re
import logging
from typing import List, Optional

from sqlmodel import Session
from fastapi import HTTPException, UploadFile

from repositories.speech_repository import SpeechRepository
from tts_model.local_model import TTSLocalModel
from schemas import TextInput
from models import SpeechRecord
from core.config import AUDIO_OUTPUT_DIR
from utils import ensure_output_folder_exists
from join_audios import combine_audio_files

logger = logging.getLogger(__name__)


class SpeechService:
    def __init__(self, tts_model: TTSLocalModel, speech_repo: SpeechRepository):
        self.tts_model = tts_model
        self.speech_repo = speech_repo
        self.audio_output_dir = ensure_output_folder_exists()

    def _generate_unique_audio_filename(self, extension=".wav") -> str:
        return f"{str(uuid.uuid4())}{extension}"

    def synthesize_speech(
        self, text_input: TextInput, db_session: Session
    ) -> SpeechRecord:
        audio_filename = self._generate_unique_audio_filename()
        output_path = os.path.join(self.audio_output_dir, audio_filename)

        try:
            self.tts_model.synthetic_voice(text_input.text, output_path=output_path)
            logger.info(f"Audio generated and saved to {output_path}")
        except Exception as e:
            logger.error(f"Error during TTS synthesis: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error synthesizing audio: {str(e)}"
            )

        try:
            db_record = self.speech_repo.create(
                db=db_session,
                text=text_input.text,
                audio_file_name=audio_filename,
            )
            return db_record
        except Exception as e:
            logger.error(f"Error saving record to DB: {str(e)}")
            # Attempt to clean up orphaned audio file if DB save fails
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                    logger.info(f"Cleaned up orphaned audio file: {output_path}")
                except OSError as oe:
                    logger.error(
                        f"Error cleaning up orphaned audio file {output_path}: {oe}"
                    )
            raise HTTPException(
                status_code=500, detail=f"Error saving record to database: {str(e)}"
            )

    def _split_text(self, text: str, max_segment_length: int = 250) -> List[str]:
        if not text:
            return []

        # Split by paragraphs first, then by sentences/clauses.
        # Regex splits by '.', ',', ';', '?', '!' but keeps them if followed by a digit (e.g. version 2.0)
        # and also splits by newline characters (single or multiple).
        segments = re.split(r"(\n\n+|\n|\.(?!\d)|,(?!\d)|;|\?(?!\d)|!(?!\d))", text)

        processed_segments = []
        current_segment = ""
        for i in range(0, len(segments), 2):
            part = segments[i]
            delimiter = segments[i + 1] if i + 1 < len(segments) else ""

            if (
                not part.strip() and not delimiter.strip()
            ):  # Avoid empty parts from multiple delimiters
                continue

            # Check if adding the current part exceeds max length
            if (
                len(current_segment) + len(part) + len(delimiter) > max_segment_length
                and current_segment
            ):
                processed_segments.append(current_segment.strip())
                current_segment = part + delimiter
            else:
                current_segment += part + delimiter

        if current_segment.strip():
            processed_segments.append(current_segment.strip())

        # Further split any segment that is still too long (e.g., a long paragraph without punctuation)
        final_segments = []
        for seg in processed_segments:
            if len(seg) > max_segment_length:
                # Simple split by max_length if no other delimiters are found
                # This is a fallback and might split words, ideal TTS would handle this gracefully or require more sophisticated splitting
                for i in range(0, len(seg), max_segment_length):
                    chunk = seg[i : i + max_segment_length].strip()
                    if chunk:
                        final_segments.append(chunk)
            elif seg.strip():  # Ensure no empty segments are added
                final_segments.append(seg.strip())

        return [
            s for s in final_segments if s
        ]  # Filter out any remaining empty strings

    def synthesize_paragraphs(
        self, text_input: TextInput, db_session: Session
    ) -> SpeechRecord:
        paragraphs = self._split_text(text_input.text)

        if not paragraphs:
            raise HTTPException(
                status_code=400,
                detail="Input text is empty or results in no processable segments.",
            )

        audio_files_paths = []
        temp_files_to_clean = []

        try:
            for i, paragraph_text in enumerate(paragraphs):
                if not paragraph_text.strip():
                    continue

                segment_filename = self._generate_unique_audio_filename(f"_seg_{i}.wav")
                segment_output_path = os.path.join(
                    self.audio_output_dir, segment_filename
                )

                try:
                    waveform = self.tts_model._sintetic_voice(
                        paragraph_text
                    )  # Assuming this returns waveform
                    self.tts_model.save_waveform(waveform, segment_output_path)
                    audio_files_paths.append(segment_output_path)
                    temp_files_to_clean.append(
                        segment_output_path
                    )  # Mark for cleanup after combining
                    logger.info(
                        f"Audio generated for segment {i + 1}/{len(paragraphs)}: {segment_output_path}"
                    )
                except Exception as e:
                    logger.error(
                        f"Error processing segment {i} ('{paragraph_text[:50]}...'): {str(e)}"
                    )
                    # Decide if we should continue or fail all. For now, let's try to continue.
                    # If many fail, we might end up with no audio_files_paths.
                    continue

            if not audio_files_paths:
                raise HTTPException(
                    status_code=500, detail="No audio segments could be generated."
                )

            final_audio_filename: str
            final_output_path: str

            if len(audio_files_paths) == 1:
                # If only one segment, use it directly
                final_output_path = audio_files_paths[0]
                final_audio_filename = os.path.basename(final_output_path)
                # The segment file is now the final file, so don't clean it up from temp_files_to_clean
                if final_output_path in temp_files_to_clean:
                    temp_files_to_clean.remove(final_output_path)
                logger.info(
                    f"Single audio segment, using directly: {final_output_path}"
                )
            else:
                # Combine multiple audio files
                combined_filename_base = (
                    self._generate_unique_audio_filename()
                )  # Gives UUID.wav
                final_output_path = os.path.join(
                    self.audio_output_dir, combined_filename_base
                )

                combined_path_result = combine_audio_files(
                    audio_files_paths, final_output_path
                )
                if not combined_path_result or not os.path.exists(combined_path_result):
                    logger.error(
                        f"Failed to combine audio files. Result: {combined_path_result}"
                    )
                    raise HTTPException(
                        status_code=500, detail="Error combining audio segments."
                    )
                final_audio_filename = os.path.basename(combined_path_result)
                logger.info(f"Audio segments combined into: {final_output_path}")

            # Create database record
            db_record = self.speech_repo.create(
                db=db_session,
                text=text_input.text,
                audio_file_name=final_audio_filename,
            )
            return db_record

        except HTTPException:
            raise  # Re-raise HTTPExceptions directly
        except Exception as e:
            logger.error(f"Generic error in synthesize_paragraphs: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error in paragraph processing: {str(e)}"
            )
        finally:
            # Clean up temporary segment files if they were combined
            if len(audio_files_paths) > 1:  # Only clean if combination happened
                for file_path in temp_files_to_clean:
                    if (
                        os.path.exists(file_path) and file_path != final_output_path
                    ):  # Ensure not deleting the final combined file if it was a segment
                        try:
                            os.remove(file_path)
                            logger.info(
                                f"Cleaned up temporary segment file: {file_path}"
                            )
                        except OSError as oe:
                            logger.error(
                                f"Error cleaning up temp file {file_path}: {oe}"
                            )

    async def synthesize_from_file(
        self, file: UploadFile, db_session: Session
    ) -> SpeechRecord:
        if not file.filename.endswith(".txt"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only .txt files are allowed.",
            )

        contents = await file.read()
        try:
            text = contents.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = contents.decode("latin-1")  # Fallback for other common encodings
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Could not decode file content. Please use UTF-8 or Latin-1 encoding.",
                )

        if not text.strip():
            raise HTTPException(status_code=400, detail="The provided file is empty.")

        text_input = TextInput(text=text)
        # Reuse the paragraph synthesis logic
        return self.synthesize_paragraphs(text_input=text_input, db_session=db_session)

    def get_records(
        self,
        db_session: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> List[SpeechRecord]:
        if search:
            return self.speech_repo.get_by_text_search(
                db=db_session, search_text=search, skip=skip, limit=limit
            )
        return self.speech_repo.get_multi(db=db_session, skip=skip, limit=limit)

    def delete_record(
        self, record_id: str, db_session: Session
    ) -> Optional[SpeechRecord]:
        record = self.speech_repo.get_by_id(db=db_session, record_id=record_id)
        if not record:
            return None  # Will be handled as 404 in the router

        audio_file_path = os.path.join(self.audio_output_dir, record.audio_file)

        deleted_record = self.speech_repo.delete(db=db_session, record_id=record_id)

        if deleted_record:
            if os.path.exists(audio_file_path):
                try:
                    os.remove(audio_file_path)
                    logger.info(f"Deleted audio file: {audio_file_path}")
                except OSError as e:
                    logger.error(
                        f"Error deleting audio file {audio_file_path}: {str(e)}"
                    )
                    # Non-critical if DB record is deleted but file stays, but log it.
            else:
                logger.warning(f"Audio file not found for deletion: {audio_file_path}")
        return deleted_record

    def update_record_text(
        self, record_id: str, text_input: TextInput, db_session: Session
    ) -> Optional[SpeechRecord]:
        # Note: This only updates the text. It does not regenerate the audio.
        # If audio regeneration is needed, that would be a more complex operation:
        # 1. Fetch old record to get audio_file name.
        # 2. Delete old audio file.
        # 3. Synthesize new audio with new text, getting a new audio_file name.
        # 4. Update record in DB with new text and new audio_file name.
        # For now, sticking to the original behavior of only updating text.

        record = self.speech_repo.update_text(
            db=db_session, record_id=record_id, new_text=text_input.text
        )
        if not record:
            # Will be handled as 404 in the router
            return None
        return record

    async def get_audio(self, record_id: str, db_session: Session) -> Optional[bytes]:
        record = self.speech_repo.get_by_id(db=db_session, record_id=record_id)
        if not record:
            return None
        audio_file_path = os.path.join(self.audio_output_dir, record.audio_file)
        if not os.path.exists(audio_file_path):
            return None
        with open(audio_file_path, "rb", encoding="utf-8") as audio_file:
            return audio_file.read()

    async def get_by_id(
        self, record_id: str, db_session: Session
    ) -> Optional[SpeechRecord]:
        return self.speech_repo.get_by_id(db=db_session, record_id=record_id)
