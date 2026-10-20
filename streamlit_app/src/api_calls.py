import streamlit as st
import requests
from config import URL_BACKEND


# Funciones para interactuar con el backend
def synthesize_speech(text: str):
    try:
        response = requests.post(
            f"{URL_BACKEND}/synthesize_paragraphs/", json={"text": text}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al generar el audio: {e}")
        return None


def synthesize_speech_file(file):
    """
    curl -X 'POST' \
  'http://localhost:8989/api/v1/synthesize_file/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@<file-name>.txt;type=text/plain'
    """
    try:
        response = requests.post(
            f"{URL_BACKEND}/synthesize_file/", files={"file": file}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al generar el audio: {e}")
        return None


def get_records(search: str = ""):
    try:
        params = {"search": search} if search else {}
        response = requests.get(f"{URL_BACKEND}/records/", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al obtener los registros: {e}")
        return []


def delete_record(record_id: str):
    try:
        response = requests.delete(f"{URL_BACKEND}/records/{record_id}")
        response.raise_for_status()
        st.success("Registro eliminado exitosamente!")
    except requests.exceptions.RequestException as e:
        st.error(f"Error al eliminar el registro: {e}")


def update_record(record_id: str, new_text: str):
    try:
        response = requests.put(
            f"{URL_BACKEND}/records/{record_id}", json={"text": new_text}
        )
        response.raise_for_status()
        st.success("Texto actualizado exitosamente!")
    except requests.exceptions.RequestException as e:
        st.error(f"Error al actualizar el texto: {e}")


def get_audio(record_id: str):
    try:
        response = requests.get(f"{URL_BACKEND}/audio/{record_id}")
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        st.error(f"Error al obtener el audio: {e}")
        return None


def get_record_details(record_id: str):
    try:
        response = requests.get(f"{URL_BACKEND}/records/{record_id}")
        response.raise_for_status()
        # Asumimos que el JSON de respuesta contiene el campo 'text'
        # por ejemplo: {"id": "...", "text": "...", "created_at": "..."}
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al obtener los detalles del registro: {e}")
        return None
