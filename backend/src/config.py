import os 

LOCAL_DEVELOPMENT = os.environ["LOCAL_DEVELOPMENT"]
LIBSQL_URL = os.getenv("LIBSQL_URL")
LIBSQL_AUTH_TOKEN = os.getenv("LIBSQL_AUTH_TOKEN")
LAMBDA_ENDPOINT = os.getenv("LAMBDA_ENDPOINT")

if LOCAL_DEVELOPMENT:
    DATABASE_URL = "sqlite:///./speech_records.db"
elif (LIBSQL_URL is None or LIBSQL_AUTH_TOKEN is None) :
    print("No se encontraron las variables de entorno")
    DATABASE_URL = "sqlite:///./speech_records.db"
else:
    DATABASE_URL = f"sqlite+{LIBSQL_URL}/?authToken={LIBSQL_AUTH_TOKEN}&secure=true"
    if not LAMBDA_ENDPOINT:
                raise EnvironmentError("LAMBDA_ENDPOINT is not set in environment variables.")