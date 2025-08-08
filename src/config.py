import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Application Configuration
APP_TITLE = "Voice Analysis Toolkit"
APP_DESCRIPTION = (
    "Upload an audio file to transcribe, summarize, analyze sentiment, "
    "and ask questions about its content. All processing is done locally "
    "and your data remains private."
)

# Model Configuration
MODEL_PROVIDER = "local"  # Set to 'local' or 'openai'

# Local model settings (if MODEL_PROVIDER is 'local')
LOCAL_TRANSCRIPTION_MODEL = "openai/whisper-base.en" 
LOCAL_ANALYSIS_MODEL = "microsoft/Phi-3-mini-4k-instruct"

# OpenAI API settings (if MODEL_PROVIDER is 'openai')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_TRANSCRIPTION_MODEL = "whisper-1"
OPENAI_ANALYSIS_MODEL = "gpt-3.5-turbo"

# File Validation Configuration
# Maximum file size in megabytes (MB)
MAX_FILE_SIZE_MB = 25 
# Maximum audio duration in minutes
MAX_FILE_LENGTH_MINS = 10
# List of allowed audio file extensions (add more as needed)
ALLOWED_FILE_EXTENSIONS = [".mp3", ".wav", ".m4a", ".flac", ".ogg"]

# Logging Configuration
LOG_FILE_PATH = "logs/app.log"
LOG_LEVEL = "INFO" # Can be "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
