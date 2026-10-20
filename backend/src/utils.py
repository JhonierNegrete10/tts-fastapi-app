import os
import logging
from core.config import AUDIO_OUTPUT_DIR

logger = logging.getLogger(__name__)

def ensure_output_folder_exists():
    """
    Ensures the base audio output folder exists.
    """
    if not os.path.exists(AUDIO_OUTPUT_DIR):
        os.makedirs(AUDIO_OUTPUT_DIR)
        logger.info(f"Audio output directory created: {AUDIO_OUTPUT_DIR}")
    return AUDIO_OUTPUT_DIR  