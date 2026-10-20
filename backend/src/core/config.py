import os

AUDIO_OUTPUT_DIR = os.getenv("AUDIO_OUTPUT_DIR", "/audio_output")

# Ensure the output directory exists
if not os.path.exists(AUDIO_OUTPUT_DIR):
    os.makedirs(AUDIO_OUTPUT_DIR) 