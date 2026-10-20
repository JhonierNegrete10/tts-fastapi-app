import streamlit as st
import torch
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from TTS.utils.generic_utils import get_user_data_dir
from TTS.utils.manage import ModelManager
import os
import tempfile
import random


def get_models():
    tts_manager = TTS().list_models()
    all_models = tts_manager.list_models()
    processed_models = []
    # print(all_models)
    for model in all_models:
        parts = model.split("/")
        if len(parts) >= 4:
            type_, language, dataset, model_name = parts[:4]
            processed_models.append(
                {
                    "full_name": model,
                    "type": type_,
                    "language": language,
                    "dataset": dataset,
                    "model_name": model_name,
                }
            )
    return processed_models


def get_speakers_list(model_name):
    tts = TTS(model_name)
    all_speakers = tts.synthesizer.tts_model.speaker_manager.name_to_id
    return [*all_speakers]


def filter_models(models, type_filter, language_filter):
    return [
        m
        for m in models
        if (not type_filter or m["type"] == type_filter)
        and (not language_filter or m["language"] == language_filter)
    ]


def random_name_output(folder="output"):
    while True:
        result = folder + "/output_" + str(random.randint(1, 1000)) + ".wav"
        if not os.path.exists(result):
            break
    return result


def generate_audio(text, model_name, language="en", speaker=None):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    output_file_path = random_name_output()

    tts = TTS((model_name), progress_bar=True).to(device)
    if tts.is_multi_speaker:
        tts.tts_to_file(
            text=text, speaker=speaker, language=language, file_path=output_file_path
        )
    else:
        tts.tts_to_file(text=text, file_path=output_file_path)

    return output_file_path


def main():
    st.title("Text-to-Speech con Coqui TTS")

    models = get_models()

    # Filtros
    type_filter = st.selectbox(
        "Filtrar por tipo", [""] + list(set(m["type"] for m in models))
    )
    language_filter = st.selectbox(
        "Filtrar por idioma", [""] + list(set(m["language"] for m in models))
    )

    # Lista de modelos filtrada
    filtered_models = filter_models(models, type_filter, language_filter)
    selected_model = st.selectbox(
        "Seleccionar modelo", [m["full_name"] for m in filtered_models]
    )

    if selected_model:
        tts = TTS(selected_model)
        if tts.is_multi_speaker:
            speakers = tts.synthesizer.tts_model.speaker_manager.name_to_id
            selected_speaker = st.selectbox("Seleccionar locutor", speakers)
        else:
            selected_speaker = None

    # Entrada de texto
    text_input = st.text_area("Ingrese el texto a convertir en audio")

    # Botón para generar audio
    if st.button("Generar Audio"):
        if text_input and selected_model:
            st.write(f"Generando audio de {text_input} con modelo {selected_model}...")
            with st.spinner("Generando audio..."):
                audio_file = generate_audio(
                    text_input,
                    selected_model,
                    filtered_models[0]["language"],
                    selected_speaker,
                )

            st.audio(audio_file, format="audio/wav")

            with open(audio_file, "rb") as file:
                btn = st.download_button(
                    label="Descargar audio",
                    data=file,
                    file_name="tts_output.wav",
                    mime="audio/wav",
                )

            # Eliminar el archivo temporal
            os.unlink(audio_file)
        else:
            st.warning("Por favor, ingrese texto y seleccione un modelo.")


if __name__ == "__main__":
    main()
