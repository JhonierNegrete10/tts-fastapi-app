#!/bin/bash

# Iniciar Jupyter Lab en segundo plano
jupyter lab --ip=0.0.0.0 --no-browser --port=8888 --allow-root > jupyter_output.log 2>&1 &

# Esperar un momento para asegurarse de que Jupyter Lab esté en funcionamiento
sleep 5

# Extraer el token de la salida y guardarlo en un archivo
TOKEN=$(grep -o 'token=[^ ]*' jupyter_output.log | cut -d'=' -f2 | head -n 1)
echo "Token de Jupyter Lab: $TOKEN" > jupyter_token.txt
echo "Token de Jupyter Lab: $TOKEN"
# Iniciar Streamlit
streamlit run main_streamlit.py