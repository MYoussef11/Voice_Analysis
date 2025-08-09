import torch
from transformers import pipeline, Pipeline
from openai import OpenAI, OpenAIError
from src import config
from src.utils.exceptions import TranscriptionError
from src.logging_config import logger


class TranscriptionService:
    """
    A service class for handling audio transcription.
    It can use either a local model or the OpenAI API based on the configuration.
    """
    _local_pipeline: Pipeline = None

    @classmethod
    def _get_local_pipeline(cls) -> Pipeline:
        """
        Initializes and returns the local transcription pipeline.
        This method uses a class-level variable to cache the pipeline,
        ensuring the model is loaded only once.
        """
        if cls._local_pipeline is None:
            try:
                logger.info(
                    f"Initializing local transcription model: {config.LOCAL_TRANSCRIPTION_MODEL}"
                )
                # Check for GPU availability
                device = "cuda:0" if torch.cuda.is_available() else "cpu"
                logger.info(f"Using device: {device} for transcription.")
                
                cls._local_pipeline = pipeline(
                    "automatic-speech-recognition",
                    model=config.LOCAL_TRANSCRIPTION_MODEL,
                    device=device
                )
                logger.info("Local transcription model initialized successfully.")
            except Exception as e:
                logger.critical(f"Failed to load local transcription model: {e}", exc_info=True)
                raise TranscriptionError(
                    "Could not initialize the local transcription model. "
                    "Please check model name and dependencies."
                )
        return cls._local_pipeline

    def _transcribe_local(self, file_path: str) -> str:
        """
        Transcribes audio using a local Hugging Face model.
        """
        try:
            logger.info(f"Starting local transcription for {file_path}")
            pipeline = self._get_local_pipeline()
            # The pipeline handles chunking for long audio files automatically
            result = pipeline(file_path)
            transcript_text = result["text"].strip()
            logger.info(f"Local transcription successful for {file_path}")
            return transcript_text
        except Exception as e:
            logger.error(f"Error during local transcription for {file_path}: {e}", exc_info=True)
            raise TranscriptionError("An unexpected error occurred during local transcription.")

    def _transcribe_openai(self, file_path: str) -> str:
        """
        Transcribes audio using the OpenAI API.
        """
        if not config.OPENAI_API_KEY:
            logger.error("OpenAI API key not found for transcription.")
            raise TranscriptionError("OpenAI API key is not configured.")
        
        try:
            logger.info(f"Sending transcription request to OpenAI for {file_path}")
            client = OpenAI(api_key=config.OPENAI_API_KEY)
            
            with open(file_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model=config.OPENAI_TRANSCRIPTION_MODEL,
                    file=audio_file
                )
            
            transcript_text = transcript.text.strip()
            logger.info(f"OpenAI transcription successful for {file_path}")
            return transcript_text
        except OpenAIError as e:
            logger.error(f"OpenAI API error during transcription for {file_path}: {e.response.text}", exc_info=True)
            raise TranscriptionError(f"An OpenAI API error occurred: {e.response.status_code}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during OpenAI transcription for {file_path}: {e}", exc_info=True)
            raise TranscriptionError("An unexpected error occurred while using the OpenAI API.")


    def transcribe(self, file_path: str) -> str:
        """
        Public method to transcribe an audio file.
        Delegates to the appropriate method based on the MODEL_PROVIDER config.

        Args:
            file_path: The path to the audio file to be transcribed.

        Returns:
            The transcribed text as a string.
        
        Raises:
            TranscriptionError: If the transcription process fails.
            ValueError: If the configured MODEL_PROVIDER is invalid.
        """
        provider = config.MODEL_PROVIDER.lower()
        logger.info(f"Transcription requested with provider: {provider}")

        if provider == 'local':
            return self._transcribe_local(file_path)
        elif provider == 'openai':
            return self._transcribe_openai(file_path)
        else:
            logger.error(f"Invalid MODEL_PROVIDER configured: {config.MODEL_PROVIDER}")
            raise ValueError(f"Invalid model provider '{config.MODEL_PROVIDER}' specified in config.")
