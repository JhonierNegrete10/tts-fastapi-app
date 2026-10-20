# Estado y features del proyecto TTS

Documento único de estado, funcionalidades, casos de uso, riesgos y propuestas del proyecto **TTS** (Text-to-Speech).

---

## 1. Estado del proyecto

### Dependencias

- **Gestión**: `pyproject.toml` en la raíz (uv, Python ≥3.10). El backend usa además `backend/requirements.txt` y `backend/requirements.deploy.txt` para Docker.
- **Principales librerías** (según `pyproject.toml` y `backend/requirements.txt`):
  - **API y servidor**: FastAPI ≥0.115.12, uvicorn ≥0.34.2, python-multipart.
  - **ML/TTS**: torch ≥2.7.0 (índice CUDA 128 en no-Darwin), transformers ≥4.51.3, scipy, numpy.
  - **Base de datos**: sqlmodel ≥0.0.24, sqlalchemy-libsql ≥0.1.0.
  - **Frontend**: streamlit ≥1.45.1.
  - **AWS**: boto3 ≥1.38.18, boto3-stubs[essential]; mangum ≥0.19.0 (solo en Lambda).
  - **Otros**: requests, pydub (en requirements del backend, no en pyproject), python-dotenv, pydantic-settings.

### Estructura de carpetas

```
TTS/
├── backend/
│   ├── src/
│   │   ├── main.py                 # FastAPI app, health, routers
│   │   ├── config.py               # DATABASE_URL, LAMBDA_ENDPOINT, LIBSQL_*
│   │   ├── core/config.py         # AUDIO_OUTPUT_DIR
│   │   ├── database.py            # SQLModel engine, create_db_and_tables, get_session
│   │   ├── models.py               # SpeechRecord (SQLModel)
│   │   ├── schemas.py              # TextInput, SpeechRecord (Pydantic), SpeechRecordOutput
│   │   ├── utils.py                # ensure_output_folder_exists
│   │   ├── join_audios.py         # combine_audio_files (pydub), find_audio_files
│   │   ├── wac_to_mp3.py          # convert_wav_to_mp3 (pydub), no integrado en API
│   │   ├── s3_client.py           # Código comentado (S3/get_object)
│   │   ├── api/endpoints/speech.py # Router: synthesize, synthesize_paragraphs, synthesize_file, records CRUD, audio
│   │   ├── repositories/speech_repository.py
│   │   ├── services/speech_service.py
│   │   └── tts_model/
│   │       ├── __init__.py        # TTSModel Lambda (no usado en main actual)
│   │       └── local_model.py     # TTSLocalModel (VitsTokenizer/VitsModel facebook/mms-tts-spa)
│   ├── local.Dockerfile
│   ├── deploy.Dockerfile
│   ├── requirements.txt
│   └── requirements.deploy.txt
├── streamlit_app/
│   └── src/
│       ├── main.py                # UI: pestañas Crear, Subir archivo, Historial
│       ├── api_calls.py           # requests al backend (synthesize_paragraphs, synthesize_file, records, audio)
│       ├── config.py              # URL_BACKEND (env)
│       └── utils.py               # format_datetime
├── lambdas/
│   └── fastapi-tts/
│       ├── main.py                # FastAPI + Mangum, POST /tts → S3 URL, GET /audio/{record_id}
│       ├── save_to_s3.py          # boto3 S3 put_object, save_waveform_to_s3
│       └── readme.md              # ECR, curl invocations Lambda
├── coqui_legacy/                  # Código legacy (Streamlit Coqui, MMS example)
├── output/text/convertidor_numeros.py
├── docker-compose.local.yml       # tts-app (backend), streamlit-app; GPU, volumes
├── docker-compose.deploy.yml      # tts-app, streamlit-app; deploy envs
├── devcontainer/devcontainer.json # Referencia a docker-compose.yml (no existe en raíz)
├── pyproject.toml
├── README.md                      # Vacío
└── secret.md
```

### Tests, CI y Docker

- **Tests**: No hay directorio `tests/`, ni `pytest.ini` ni referencias a pytest en el código fuente del proyecto. No hay CI (por ejemplo `.github/workflows`) configurado.
- **Docker**:
  - `docker-compose.local.yml`: servicios `tts-app` (backend con `local.Dockerfile`, puerto 8989, GPU, volumen `./audio_output:/audio_output`) y `streamlit-app` (puerto 5555→8501). Streamlit no tiene `URL_BACKEND` en env en el compose; depende de `.env` o default `http://tts-backend:8989/api/v1`.
  - `docker-compose.deploy.yml`: mismos servicios con `deploy.Dockerfile` y `deploy.env`; sin GPU explícito.
  - Backend: `local.Dockerfile` instala PyTorch CUDA y ffmpeg; `deploy.Dockerfile` usa `requirements.deploy.txt` y copia `./src` (sin montar volumen).
  - Lambda: imagen propia en `lambdas/`, Mangum para API Gateway; modelo desde `./model` (local_files_only).

### Nivel actual de documentación

- **README.md**: vacío.
- **Otra doc**: `lambdas/fastapi-tts/readme.md` (ECR, docker run, curl de invocación Lambda). No hay docs de arquitectura, API, runbook ni setup en la raíz o en `backend/`.

---

## 2. Funcionalidades actuales

Lista de lo implementado según el código (sin inventar features):

| Área | Funcionalidad | Ubicación |
|------|----------------|-----------|
| API | Síntesis de texto a voz (una frase) | `POST /api/v1/synthesize/` |
| API | Síntesis por párrafos (split + concatenación de WAV) | `POST /api/v1/synthesize_paragraphs/` |
| API | Síntesis desde archivo .txt | `POST /api/v1/synthesize_file/` |
| API | Listar registros (paginación, búsqueda por texto) | `GET /api/v1/records/` |
| API | Obtener registro por ID | `GET /api/v1/records/{record_id}` |
| API | Actualizar texto del registro (sin regenerar audio) | `PUT /api/v1/records/{record_id}` |
| API | Eliminar registro (y archivo de audio en disco) | `DELETE /api/v1/records/{record_id}` |
| API | Descarga de audio por record_id | `GET /api/v1/audio/{record_id}` (FileResponse desde `/audio_output/`) |
| API | Health check | `GET /health` |
| Backend | Modelo TTS local (Vits, facebook/mms-tts-spa) | `tts_model/local_model.py` |
| Backend | Persistencia en SQLite/LibSQL (SpeechRecord) | `models.py`, `database.py`, `repositories/speech_repository.py` |
| Backend | División de texto en segmentos (~250 caracteres) y unión de WAV | `speech_service._split_text`, `join_audios.combine_audio_files` |
| Streamlit | Crear audio desde texto | Pestaña "Crear Nuevo" → `synthesize_paragraphs` |
| Streamlit | Subir .txt y generar audio | Pestaña "Subir Archivo" |
| Streamlit | Historial con búsqueda, reproducción, edición de texto, borrado | Pestaña "Historial" |
| Lambda | Síntesis vía POST /tts y subida a S3 | `lambdas/fastapi-tts/main.py`, `save_to_s3.py` |
| Lambda | Lectura de audio desde /tmp (por record_id) | `GET /audio/{record_id}` en Lambda (no alineado con backend) |

Flujo principal actual: **Usuario → Streamlit o cliente HTTP → Backend FastAPI → TTSLocalModel (Vits) → WAV en `/audio_output` + SpeechRecord en DB → respuesta con registro y audio vía `/audio/{id}`.**

Diagrama opcional de flujo:

```mermaid
flowchart LR
  subgraph Client
    ST[Streamlit]
    API[Cliente HTTP]
  end
  subgraph Backend
    FAPI[FastAPI]
    SVC[SpeechService]
    TTS[TTSLocalModel]
    REPO[SpeechRepository]
    DB[(SQLite/LibSQL)]
    FS[/audio_output]
  end
  ST --> FAPI
  API --> FAPI
  FAPI --> SVC
  SVC --> TTS
  SVC --> REPO
  SVC --> join_audios
  REPO --> DB
  TTS --> FS
  FAPI --> FS
```

---

## 3. Casos de uso

- **Actor**: Usuario final (persona que quiere audio a partir de texto).  
- **Objetivo**: Obtener un archivo de audio (voz sintética en español) y poder listar, escuchar, editar texto y eliminar registros.

**Flujo principal**

1. Usuario escribe texto en Streamlit (o envía POST a `/api/v1/synthesize_paragraphs/`).
2. Backend divide el texto en segmentos, genera WAV por segmento con Vits, concatena con pydub, guarda el WAV en `/audio_output` y crea un `SpeechRecord` en la base de datos.
3. Usuario recibe confirmación y puede reproducir el audio (Streamlit llama a `GET /api/v1/audio/{id}`).
4. Usuario puede buscar en el historial, ver/editar texto (solo texto, sin regenerar audio) y eliminar registros.

**Flujos alternativos**

- **Archivo .txt**: Usuario sube un .txt en la pestaña "Subir Archivo" (o `POST /api/v1/synthesize_file/`); el contenido se procesa igual que en el flujo por párrafos.
- **Solo una frase**: Uso de `POST /api/v1/synthesize/` para un solo bloque de texto sin división ni concatenación.
- **Consumo solo API**: Cualquier cliente HTTP puede usar los mismos endpoints sin Streamlit.
- **Lambda**: Flujo separado: POST al Lambda `/tts` → síntesis en Lambda → subida a S3 y devolución de `s3_url`; el backend actual no usa este flujo (usa `TTSLocalModel`).

---

## 4. Edge cases y riesgos

### Casos límite y errores frecuentes

- **Texto vacío o solo blancos**: Rechazado en `synthesize_paragraphs` (400) y en `synthesize_from_file` (400). `_split_text` devuelve lista vacía → 400 "Input text is empty or results in no processable segments."
- **Archivo no .txt**: `synthesize_from_file` devuelve 400 "Invalid file type. Only .txt files are allowed."
- **Encoding del archivo**: Solo UTF-8 y Latin-1; otro encoding → 400 "Could not decode file content...".
- **Segmentos que fallan en TTS**: En `synthesize_paragraphs` si un segmento falla se registra el error y se continúa; si todos fallan → 500 "No audio segments could be generated."
- **Registro no encontrado**: `get_by_id`, `delete_record`, `update_record_text` → 404 "Record not found" desde el router.
- **Audio no encontrado en disco**: `get_audio_endpoint` usa `FileResponse(path=f"/audio_output/{record_db.audio_file}")`; si el archivo fue borrado manualmente o no existe, FileResponse puede fallar (riesgo 404/500 según versión).
- **Longitud de texto**: División por ~250 caracteres y por delimitadores; párrafos muy largos sin puntuación se parten por `max_segment_length` (posible corte en mitad de palabra).

### Dependencias críticas

- **PyTorch + CUDA**: En local/Docker con GPU; si no hay GPU, `TTSLocalModel` usa CPU (más lento).
- **ffmpeg**: Necesario para pydub en `join_audios`; instalado en los Dockerfiles del backend.
- **Modelo Vits**: `facebook/mms-tts-spa`; descarga desde Hugging Face en la primera ejecución del backend (no en Lambda, que usa `./model` local).
- **Base de datos**: SQLite por defecto; en producción con LibSQL se requieren `LIBSQL_URL` y `LIBSQL_AUTH_TOKEN`; si no están y no es local → fallback a SQLite.
- **Streamlit**: Depende de que el backend esté accesible en `URL_BACKEND` (en Docker: `http://tts-backend:8989/api/v1`). Si no se configura, el default puede no coincidir con el entorno.

### Riesgos técnicos y de mantenimiento

- **Doble fuente de dependencias**: `pyproject.toml` en raíz vs `backend/requirements.txt` y `requirements.deploy.txt`; pydub está en backend pero no en pyproject → riesgo de entornos desalineados.
- **Devcontainer**: `devcontainer.json` apunta a `../docker-compose.yml`, que no existe (existen `docker-compose.local.yml` y `docker-compose.deploy.yml`).
- **Lambda vs backend**: El backend usa solo `TTSLocalModel`; `tts_model/__init__.py` define un cliente Lambda que no se usa en `main.py`. Lambda tiene su propio endpoint `/audio/{record_id}` leyendo de `/tmp`, no integrado con la DB del backend.
- **S3 en backend**: `s3_client.py` está comentado; la descarga de audio es desde disco local (`/audio_output`). Para despliegue distribuido o sin disco persistente, haría falta S3 u otro almacenamiento.
- **LOCAL_DEVELOPMENT**: En `config.py` está fijado a `True` (# comentado `os.environ`), por lo que siempre se usa SQLite local aunque existan variables LibSQL.
- **open() con encoding en get_audio**: En `speech_service.get_audio` se usa `open(..., encoding="utf-8")` para un archivo binario; en Python 3 eso puede ser incorrecto (debería ser sin encoding o `rb`).

---

## 5. Pros y contras

### Diseño actual

- **Pros**: Separación clara router → service → repository; inyección de dependencias en FastAPI; reutilización de `synthesize_paragraphs` para texto y archivo; limpieza de segmentos temporales y de archivo al borrar registro.
- **Contras**: Router en `speech.py` define su propio `get_speech_service()` que instancia TTS y repo de nuevo, pero `main.py` lo anula con `dependency_overrides`; duplicación conceptual. El endpoint de audio asume ruta fija `/audio_output/` y FileResponse sin comprobar existencia del fichero.

### Stack

- **Pros**: FastAPI + SQLModel + Streamlit es coherente; Vits en español (mms-tts-spa); Docker con GPU para desarrollo; Lambda + Mangum para despliegue serverless opcional.
- **Contras**: Dos pilas (local vs Lambda) no unificadas; dependencias repartidas entre pyproject y requirements del backend; PyTorch/CUDA pesados para despliegue si no se usa Lambda.

### Decisiones visibles

- TTS en proceso (síncrono) en el backend; sin cola ni workers para textos muy largos.
- Almacenamiento de audio en filesystem local; no S3 en el flujo principal del backend.
- Edición de registro solo actualiza el campo texto; no se regenera el audio.
- Streamlit como única UI oficial; no hay otra capa frontend.

---

## 6. Features propuestas

| Prioridad | Mejora / feature | Descripción breve |
|-----------|------------------|-------------------|
| Alta | Unificar dependencias | Un solo origen de verdad (pyproject.toml o requirements) y documentar; añadir pydub a pyproject si el backend se instala desde raíz. |
| Alta | Corregir `get_audio` (binario) | Abrir archivo de audio en modo binario (`rb`) en `speech_service.get_audio` y, en el endpoint, comprobar existencia del archivo antes de FileResponse. |
| Alta | README mínimo | Requisitos (Python, ffmpeg, GPU opcional), cómo levantar backend + Streamlit (local y Docker), variables de entorno principales. |
| Media | Tests unitarios | Tests para `_split_text`, `combine_audio_files`, SpeechRepository y SpeechService (con DB en memoria o SQLite :memory:). |
| Media | Tests de API | Tests de integración con TestClient de FastAPI para al menos health, synthesize_paragraphs (texto corto), get records, get audio. |
| Media | Documentar API | Enlazar/redactar uso de OpenAPI (`/api/v1/openapi.json`) y describir en README o docs los endpoints y ejemplos de curl. |
| Media | Variables de entorno en compose | Definir `URL_BACKEND` para streamlit-app en `docker-compose.local.yml` (y deploy) para evitar depender de un .env no versionado. |
| Media | Runbook básico | Qué hacer si el modelo no carga, si falla la DB, si no hay espacio en disco; cómo ver logs (uvicorn, Docker). |
| Baja | CI | Pipeline (GitHub Actions u otro) que ejecute lint y tests en cada push. |
| Baja | Integración Lambda opcional | Si se quiere usar Lambda como motor TTS: configurar backend para usar `TTSModel` (Lambda) según variable de entorno y documentar flujo S3. |
| Baja | Regenerar audio al editar texto | Opción (endpoint o parámetro) para regenerar el WAV cuando se actualiza el texto del registro. |
| Baja | Arquitectura en docs | Diagrama de componentes (backend, Streamlit, Lambda, DB, almacenamiento) y decisión de cuándo usar local vs Lambda. |

---

## 7. Testing

- **Cobertura actual**: No hay tests en el repositorio (ni `tests/` ni configuración de pytest). Cobertura 0%.
- **Recomendado**:
  - **Unitarios**: `SpeechService._split_text` con distintos textos (vacío, solo espacios, muchos párrafos, longitud >250); `join_audios.combine_audio_files` con WAV de prueba; SpeechRepository con SQLite en memoria.
  - **Integración**: FastAPI `TestClient` para `GET /health`, `POST /api/v1/synthesize_paragraphs/` (texto corto, mockear o skipear TTS si es pesado), `GET /api/v1/records/`, `GET /api/v1/audio/{id}` (con fixture de registro y archivo).
  - **E2E (opcional)**: Flujo mínimo vía requests contra backend + Streamlit (o solo API) en Docker; útil para regresión antes de releases.

---

## 8. Documentación

### Gaps actuales

- README vacío: no hay descripción del proyecto ni instrucciones de ejecución.
- No hay documento de arquitectura ni diagrama de despliegue.
- Variables de entorno no están listadas en un solo sitio (backend: config.py, core/config; streamlit: config.py; Lambda: save_to_s3, main).
- API documentada solo por OpenAPI (FastAPI); no hay guía de uso ni ejemplos en docs.
- Runbook inexistente (incidencias, logs, reinicio, espacio en disco).
- Devcontainer referencia un `docker-compose.yml` que no existe.

### Propuesta mínima

1. **README**: Nombre del proyecto, propósito (TTS en español), requisitos (Python 3.10+, ffmpeg, opcional CUDA), instalación (uv/pip), ejecución local (backend + Streamlit), Docker (`docker-compose -f docker-compose.local.yml up`), variables de entorno principales (DATABASE_URL, AUDIO_OUTPUT_DIR, URL_BACKEND, LAMBDA_ENDPOINT si aplica), enlace a `/docs` para la API.
2. **API**: Mantener OpenAPI; añadir en README o en `docs/api.md` una tabla de endpoints y un ejemplo de curl por flujo (synthesize_paragraphs, get audio).
3. **Runbook**: Archivo `docs/runbook.md` con: comprobaciones de salud (health, disco, modelo cargado), logs (dónde y qué buscar), errores frecuentes (texto vacío, archivo no encontrado, encoding) y pasos básicos de recuperación.
4. **Arquitectura**: Un solo documento (p. ej. `docs/architecture.md`) con diagrama de componentes (backend, Streamlit, Lambda, DB, almacenamiento) y flujo de datos; mencionar diferencias local vs deploy vs Lambda.

---

## 9. Alternativas consideradas

- **TTS en Lambda vs en backend**: El código soporta ambos (TTSLocalModel y TTSModel Lambda). Actualmente solo se usa el modelo local; Lambda sirve para despliegue sin GPU y con salida en S3, a cambio de cold starts y límites de payload.
- **SQLite vs LibSQL**: Config permite LibSQL (Turso) vía `LIBSQL_URL` y token; el flujo por defecto es SQLite. LibSQL da persistencia distribuida y mejor adaptada a producción multi-nodo.
- **Audio en disco vs S3**: El flujo principal es disco (`/audio_output`); `s3_client.py` está comentado. S3 sería preferible para escalar horizontalmente y backups; implica cambios en escritura (synthesize) y lectura (get_audio).
- **Streamlit vs otra UI**: Streamlit es la única UI; una SPA (React/Next.js) o solo API + clientes externos serían alternativas si se necesita más control de UX o integración con otros sistemas.

---

*Documento generado a partir del codebase del proyecto TTS. Referencias a archivos y líneas corresponden al estado actual del repositorio.*
