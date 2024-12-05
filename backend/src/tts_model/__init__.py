import logging
from config import LAMBDA_ENDPOINT
import requests

logger = logging.getLogger("uvicorn.info")
logger.setLevel(logging.INFO)


class TTSModel:
    """Using AWS Lambda service with the model deployed as a FastAPI endpoint."""

    def __init__(self, lambda_endpoint: str):
        self.lambda_endpoint = f"{lambda_endpoint}?"

    def synthetic_voice(self, text: str) -> str:
        """Calls the Lambda function to synthesize voice and returns the S3 URL."""
        payload = {"text": text}
        try:
            response = requests.post(self.lambda_endpoint, json=payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request to Lambda failed: {e}")
            raise
        s3_url = response.json().get("s3_url")
        if not s3_url:
            raise ValueError("S3 URL not returned by Lambda function.")
        logger.info(f"Synthesized voice available at {s3_url}")
        return s3_url


tts_model = TTSModel(lambda_endpoint=LAMBDA_ENDPOINT)
