import streamlit as st
from api_calls import (
    synthesize_speech,
    get_records,
    delete_record,
    update_record,
    get_audio,
)

from utils import format_datetime


st.title("Conversor de Texto a Voz")


# Crear pestañas
tab_create, tab_history = st.tabs(["Crear Nuevo", "Historial"])

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

with tab_history:
    search_text = st.text_input("Buscar en los textos generados:", "")
    if st.button("Refrescar Historial") or search_text:
        records = get_records(search_text)
        for record in records:
            with st.expander(f"Texto: {record['text'][:50]}..."):
                st.write(f"Creado: {format_datetime(record['created_at'])}")
                st.write(f"Texto completo: {record['text']}")
                audio = get_audio(record["id"])
                st.audio(audio, format="audio/wav")

                # Botón para eliminar
                if st.button(
                    f"Eliminar Registro {record['id']}", key=f"delete_{record['id']}"
                ):
                    delete_record(record["id"])
                    st.rerun()

                # Funcionalidad para editar
                new_text = st.text_input(
                    "Editar texto:", value=record["text"], key=f"edit_{record['id']}"
                )
                if st.button(
                    f"Actualizar Texto {record['id']}", key=f"update_{record['id']}"
                ):
                    update_record(record["id"], new_text)
                    st.rerun()
