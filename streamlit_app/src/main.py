import streamlit as st
from api_calls import (
    synthesize_speech,
    get_records,
    delete_record,
    update_record,
    get_audio,
    synthesize_speech_file,
    get_record_details,
)

from utils import format_datetime


st.title("Conversor de Texto a Voz")


# Crear pestañas
tab_create, tab_upload, tab_history = st.tabs(
    ["Crear Nuevo", "Subir Archivo", "Historial"]
)

with tab_create:
    text_input = st.text_input(
        "Ingresa el texto para convertir a voz:", "Hola, ¿cómo estás?"
    )
    if st.button("Convertir a Voz"):
        if text_input:
            record = synthesize_speech(text_input)
            if record:
                st.success("Audio generado exitosamente!")
                audio = get_audio(record["id"])
                st.audio(audio, format="audio/wav")
        else:
            st.warning("Por favor, ingresa un texto.")

with tab_upload:
    uploaded_file = st.file_uploader(
        "Sube un archivo .txt para sintetizar", type=["txt"]
    )
    if uploaded_file is not None:
        if st.button("Convertir Archivo a Voz"):
            record = synthesize_speech_file(uploaded_file)
            if record:
                st.success("Audio del archivo generado exitosamente!")
                audio_content = get_audio(record["id"])
                if audio_content:
                    st.audio(audio_content, format="audio/wav")
                else:
                    st.error("No se pudo obtener el audio del archivo.")
            else:
                st.error("Error al procesar el archivo.")

with tab_history:
    search_text = st.text_input("Buscar en los textos generados:", "")
    if "historial_refrescado" not in st.session_state:
        st.session_state.historial_refrescado = False

    if st.button("Refrescar Historial"):
        st.session_state.historial_refrescado = True
        records = get_records(search_text)
        st.session_state.records = records
    elif search_text and not st.session_state.historial_refrescado:
        records = get_records(search_text)
        st.session_state.records = records
    elif "records" not in st.session_state and not search_text:
        records = get_records()
        st.session_state.records = records

    st.session_state.historial_refrescado = False

    if "records" in st.session_state and st.session_state.records:
        for record_summary in st.session_state.records:
            expander_title = record_summary.get(
                "name", f"Registro ID: {record_summary['id']}"
            )
            with st.expander(expander_title):
                st.write(f"Creado: {format_datetime(record_summary['created_at'])}")

                record_details = get_record_details(record_summary["id"])

                if record_details and "text" in record_details:
                    full_text = record_details["text"]
                    st.text_area(
                        "Texto completo:",
                        value=full_text,
                        height=200,
                        disabled=True,
                        key=f"display_{record_summary['id']}",
                    )

                    audio = get_audio(record_summary["id"])
                    if audio:
                        st.audio(audio, format="audio/wav")

                    if st.button(
                        f"Eliminar Registro {record_summary['id']}",
                        key=f"delete_{record_summary['id']}",
                    ):
                        delete_record(record_summary["id"])
                        del st.session_state.records
                        st.rerun()

                    new_text = st.text_area(
                        "Editar texto:",
                        value=full_text,
                        height=150,
                        key=f"edit_{record_summary['id']}",
                    )
                    if st.button(
                        f"Actualizar Texto {record_summary['id']}",
                        key=f"update_{record_summary['id']}",
                    ):
                        update_record(record_summary["id"], new_text)
                        del st.session_state.records
                        st.rerun()
                else:
                    st.error("No se pudo cargar el texto completo del registro.")
    elif not search_text:
        st.write(
            "No hay registros para mostrar. Intenta refrescar o crea nuevo contenido."
        )
