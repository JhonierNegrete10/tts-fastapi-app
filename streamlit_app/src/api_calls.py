import streamlit as st
import requests
from config import URL_BACKEND


# Funciones para interactuar con el backend
def synthesize_speech(text: str):
    try:
        response = requests.post(f"{URL_BACKEND}/synthesize/", json={"text": text})
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