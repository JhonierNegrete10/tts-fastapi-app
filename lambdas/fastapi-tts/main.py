import torch
import scipy.io.wavfile
import os
import uuid
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from mangum import Mangum
from transformers import VitsTokenizer, VitsModel, set_seed
from pydantic import BaseModel
from dotenv import load_dotenv
from save_to_s3 import save_waveform_to_s3

load_dotenv()

# Set deterministic behavior
set_seed(555)

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logger = logging.getLogger("uvicorn.info")
logger.setLevel(logging.INFO)


class TTSPayload(BaseModel):
    text: str


class TTSModel:
    def __init__(self):
        try:
            self.tokenizer = VitsTokenizer.from_pretrained(
                "./model", local_files_only=True
            )
            self.model = VitsModel.from_pretrained("./model", local_files_only=True)
            logger.info("TTS model loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading TTS model: {e}")
            raise

    def synthetic_voice(self, text: str):
        try:
            inputs = self.tokenizer(text, return_tensors="pt")
            with torch.no_grad():
                output = self.model(**inputs).waveform
            return output
        except Exception as e:
            logger.error(f"Error during synthesis: {e}")
            raise


# Instantiate the TTS model
tts_model = TTSModel()


@app.post("/tts")
def synthetic_voice(payload: TTSPayload):
    try:
        logger.info(f"Received text for synthesis: {payload.text}")
        waveform = tts_model.synthetic_voice(payload.text)
    except Exception as e:
        logger.error(f"Error during voice synthesis: {e}")
        raise HTTPException(status_code=500, detail="Failed to synthesize voice.")

    filename = f"{uuid.uuid4()}.wav"
    # todo: cambiar a /tmp/ para que funcione en lambda
    # lambda_path = "./" + filename # local path
    lambda_path = f"/tmp/{filename}"
    logger.info(f"Generated filename: {filename}")

    try:
        scipy.io.wavfile.write(
            lambda_path,
            tts_model.model.config.sampling_rate,
            data=waveform.numpy().squeeze(),
        )
        logger.info(f"Waveform written to temporary file: {lambda_path}")
    except Exception as e:
        logger.error(f"Error writing waveform to file: {e}")
        raise HTTPException(status_code=500, detail="Failed to write waveform to file.")

    try:
        with open(lambda_path, "rb") as f:
            waveform_bytes = f.read()

        logger.info(f"Read waveform bytes from file: {lambda_path}")
    except Exception as e:
        logger.error(f"Error reading waveform file: {e}")
        raise HTTPException(status_code=500, detail="Failed to read waveform file.")

    try:
        s3_url = save_waveform_to_s3(waveform_bytes, filename)
    except Exception as e:
        logger.error(f"Error uploading waveform to S3: {e}")

    # try:
    #     os.remove(lambda_path)
    #     logger.info(f"Temporary file removed: {lambda_path}")
    # except Exception as e:
    #     logger.error(f"Error removing temporary file: {e}")
    return {"s3_url": s3_url}


@app.get("/audio/{record_id}")
async def get_audio(record_id: str):
    # search if exst in tmp
    temporary_audio_path = f"/tmp/{record_id}.wav"
    if not os.path.exists(temporary_audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")

    return FileResponse(temporary_audio_path, media_type="audio/wav")


# Create the Mangum handler
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
    # docker comando para correr el contenedor
    # docker run -p 8000:8000 fastapi-tts:latest

    # docker comando para construir la imagen
    # docker build -t fastapi-tts:latest .
