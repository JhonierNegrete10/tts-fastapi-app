from fastapi import FastAPI, Depends
import uvicorn
import logging
import os
from database import create_db_and_tables
from tts_model.local_model import TTSLocalModel
from repositories.speech_repository import SpeechRepository
from services.speech_service import SpeechService
from api.endpoints import speech as speech_router


# Configure logging
# Set a basic config if not already set by uvicorn or other means
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO").upper())
logger = logging.getLogger("uvicorn.info")  # Standard uvicorn logger

app = FastAPI(
    title="Text-to-Speech API",
    description="API for synthesizing speech from text and managing audio records.",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",  # OpenAPI schema path
)

# --- Dependency Management ---
# These instances are created once when the application starts up and shared across requests.

# Initialize TTS Model
# If TTSLocalModel has heavy initialization, consider doing it within on_startup
# or ensure it's lightweight enough for global scope instantiation.
tts_model_instance = TTSLocalModel()

# Initialize Repository
speech_repository_instance = SpeechRepository()

# Initialize Service with its dependencies
speech_service_instance = SpeechService(
    tts_model=tts_model_instance, speech_repo=speech_repository_instance
)


# Dependency provider function for SpeechService
# FastAPI will call this function to inject the shared service instance into path operation functions
# that depend on `get_speech_service` (as defined in the router module).
def get_speech_service_dependency() -> SpeechService:
    return speech_service_instance


# --- Event Handlers ---
@app.on_event("startup")
def on_startup():
    logger.info(
        "Application startup: Creating database and tables if they don't exist."
    )
    create_db_and_tables()
    # Example: Ensure output directory from config exists (if not handled by service init)
    # from core.config import AUDIO_OUTPUT_DIR
    # if not os.path.exists(AUDIO_OUTPUT_DIR):
    #     os.makedirs(AUDIO_OUTPUT_DIR)
    #     logger.info(f"Audio output directory ensured: {AUDIO_OUTPUT_DIR}")
    logger.info("Startup complete.")


@app.on_event("shutdown")
def on_shutdown():
    logger.info("Application shutdown.")
    # Add any cleanup logic here if necessary (e.g., closing database connections if not managed automatically)


# --- Include Routers ---
# Mount the API endpoints from the speech router module.
app.include_router(
    speech_router.router,  # The APIRouter instance from api.endpoints.speech
    prefix="/api/v1",  # All routes in this router will be prefixed with /api/v1
    tags=["Speech Synthesis"],  # Tag for grouping endpoints in OpenAPI documentation
)

# Override the dependency for `get_speech_service` used in the router.
# This tells FastAPI: whenever a path operation depends on `speech_router.get_speech_service`,
# actually provide the instance returned by `get_speech_service_dependency` (our singleton).
app.dependency_overrides[speech_router.get_speech_service] = (
    get_speech_service_dependency
)


# --- Health Check Endpoint (Recommended) ---
@app.get("/health", tags=["Utilities"])
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "healthy", "message": "Application is running smoothly."}


# --- Main Execution Block (for running with `python main.py`) ---
if __name__ == "__main__":
    port = int(
        os.environ.get("PORT", 8989)
    )  # Allow port to be set by environment variable
    reload_app = (
        os.environ.get("RELOAD_APP", "True").lower() == "true"
    )  # Control reload via env

    # Uvicorn logging configuration (customize as needed)
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = (
        '%(asctime)s %(levelname)s [%(name)s:%(lineno)d] [PID:%(process)d] - "%(request_line)s" %(status_code)s'
    )
    log_config["formatters"]["default"]["fmt"] = (
        "%(asctime)s %(levelname)s [%(name)s:%(lineno)d] [PID:%(process)d] - %(message)s"
    )
    log_config["loggers"]["uvicorn"]["level"] = "INFO"
    log_config["loggers"]["uvicorn.error"]["level"] = "INFO"
    log_config["loggers"]["uvicorn.access"]["level"] = (
        "INFO"  # Set to WARNING for less verbose access logs
    )

    uvicorn.run(
        "main:app",  # Path to the FastAPI app object (filename:variable_name)
        host="0.0.0.0",  # Listen on all available network interfaces
        port=port,
        reload=reload_app,  # Enable auto-reload for development
        reload_delay=2,  # Delay before reloading
        log_config=log_config,  # Apply the custom logging configuration
    )
