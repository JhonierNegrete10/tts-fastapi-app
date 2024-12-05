import os

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

# URL del backend de FastAPI
URL_BACKEND = os.getenv("URL_BACKEND", "http://tts-backend:8989")