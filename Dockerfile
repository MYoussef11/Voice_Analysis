# Use the official Python 3.10 slim-buster image as a lightweight base
FROM python:3.10-slim

# Set the application's working directory inside the container
WORKDIR /app

# Install essential system-level dependencies
# - ffmpeg: Required by the pydub library for audio processing
# - git: Required by some pip packages for installation from version control
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the dependency file first to leverage Docker's layer caching
COPY requirements.txt .

# Install Python packages, disabling the cache to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code into the container
# force a re-installation of all packages
COPY src/ src/

# Expose the port Gradio will run on, making it accessible to the host
EXPOSE 7860

# Set the environment variable for the Ollama host when running inside Docker.
ENV OLLAMA_HOST=host.docker.internal

# Define the default command to run when the container starts
# Uses Python's module flag '-m' for correct package path resolution
CMD ["python", "-m", "src.app"]