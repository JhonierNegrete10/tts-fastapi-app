# save to s3 function
import os
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)
# Initialize S3 client
s3_client = boto3.client("s3")
S3_BUCKET = os.getenv(
    "S3_BUCKET_NAME", "tts-fastapi"
)  # Ensure this environment variable is set
S3_FOLDER = os.getenv(
    "S3_FOLDER_NAME", "audios"
)  # Ensure this environment variable is set


def save_waveform_to_s3(waveform_bytes: bytes, filename: str) -> str:
    try:
        
        s3_full_path = f"{S3_FOLDER}/{filename}"
        s3_client.put_object(
            Bucket=f"{S3_BUCKET}", Key=s3_full_path, Body=waveform_bytes, ContentType="audio/wav"
        )
        s3_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{s3_full_path}"
        logger.info(f"Waveform successfully uploaded to {s3_url}")
        return s3_url
    except Exception as e:
        logger.error(f"Failed to upload waveform to S3: {e}")
