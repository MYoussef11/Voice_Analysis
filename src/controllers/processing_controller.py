from src.services.transcription_service import TranscriptionService
from src.services.analysis_service import AnalysisService
from src.utils.validator import Validator
from src.utils.exceptions import AppError
from src.logging_config import logger


class ProcessingController:
    """
    The central controller that orchestrates the entire analysis process.
    It manages the application's state and coordinates the services.
    """
    def __init__(self):
        """
        Initializes the controller and its required services.
        """
        self.transcription_service = TranscriptionService()
        self.analysis_service = AnalysisService()
        self.validator = Validator()
        self.transcript: str | None = None
        self.chat_history: list = []
        logger.info("ProcessingController initialized.")

    def process_audio_file(self, file_path: str):
        """
        The main workflow method. It validates and transcribes the audio file.
        This method prepares the controller for on-demand analysis.

        Args:
            file_path: The path to the temporary audio file uploaded by the user.

        Raises:
            AppError: If any step in the validation or transcription fails.
        """
        try:
            # Reset state for a new file
            self.transcript = None
            self.chat_history = []
            logger.info(f"Starting processing for audio file: {file_path}")

            # 1. Validate the file
            self.validator.validate_audio_file(file_path)

            # 2. Transcribe the file
            self.transcript = self.transcription_service.transcribe(file_path)

            logger.info(f"Successfully processed and transcribed file: {file_path}")

        except AppError as e:
            # Catch our known application errors, log them, and re-raise
            logger.error(f"An application error occurred during processing: {e}", exc_info=True)
            raise e
        except Exception as e:
            # Catch any other unexpected errors
            logger.critical(f"An unexpected critical error occurred: {e}", exc_info=True)
            raise AppError("An unexpected error occurred. Please check the logs.")

    def _ensure_transcript_exists(self):
        """
        A private helper to check if a transcript is ready for analysis.
        """
        if not self.transcript:
            logger.warning("Attempted to perform analysis before processing a file.")
            raise AppError("Please process an audio file before requesting analysis.")

    def get_transcript(self) -> str:
        """
        Returns the stored transcript.
        """
        self._ensure_transcript_exists()
        logger.info("Transcript requested by user.")
        return self.transcript

    def get_summary(self) -> str:
        """
        Generates a summary for the currently loaded transcript.
        """
        self._ensure_transcript_exists()
        logger.info("Summary requested by user.")
        return self.analysis_service.summarize(self.transcript)

    def get_sentiment(self) -> str:
        """
        Performs sentiment analysis on the currently loaded transcript.
        """
        self._ensure_transcript_exists()
        logger.info("Sentiment analysis requested by user.")
        return self.analysis_service.get_sentiment(self.transcript)

    def answer_question(self, question: str) -> str:
        """
        Answers a question about the currently loaded transcript.
        """
        self._ensure_transcript_exists()
        if not question or not question.strip():
            raise AppError("Question cannot be empty.")
            
        logger.info(f"Question received from user: '{question}'")
        # The entire history to the analysis service
        response = self.analysis_service.answer_question(self.transcript, question, self.chat_history)
        # Update history with the new turn
        self.chat_history.append([question, response])
        return response
    