# Use the official Python image from the Docker Hub
FROM python:3.12-slim-bullseye

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

RUN pip install --upgrade pip

# Install the pytorch dependencies
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 8989 
# # Copy the rest of the application code into the container
# COPY . .
CMD [ "python", "main.py" ]
# CMD ["sh", "-c", "start.sh"]
# ENTRYPOINT ["tail", "-f", "/dev/null"]
