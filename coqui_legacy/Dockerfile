# Use Python 3.11 as the base image
FROM ghcr.io/coqui-ai/tts

# Set the working directory in the container
WORKDIR /app

# Update and install Ubuntu packages
RUN apt-get update && apt-get upgrade -y
# RUN apt-get install -y --no-install-recommends gcc g++ make python3 python3-dev python3-pip python3-venv python3-wheel espeak-ng libsndfile1-dev && rm -rf /var/lib/apt/lists/*

RUN apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-venv \
    cmake\
    git \
    curl \
    wget \
    iputils-ping \
    net-tools \
    ffmpeg \
    && apt-get clean

# Copy the requirements file into the container
COPY requirements.txt .

RUN pip install --upgrade pip

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

#pip install --upgrade transformers accelerate
# Copy the rest of the application code
# COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501 8888
# COPY multi_start.sh .
# RUN chmod +x multi_start.sh
# ENTRYPOINT ["jupyter", "lab", "--ip=0.0.0.0","--no-browser", "--port=8888", "--allow-root"]

# Command to run the Streamlit application
# ENTRYPOINT [ "/bin/bash" ]
# command to keep alive the container
ENTRYPOINT ["tail", "-f", "/dev/null"]
# ENTRYPOINT ["streamlit", "run", "main.py"]
# Hacer el script ejecutable
# ENTRYPOINT [ "app/multi_start.sh" ]
# CMD ["sh", "-c", "streamlit run --server.port 8501 main.py"]