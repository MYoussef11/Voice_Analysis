import os
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from src import config
from src.utils.exceptions import (
    InvalidFileType,
    FileSizeExceeded,
    FileLengthExceeded,
    ValidationError
)
from src.logging_config import logger


class Validator:
    """
    A class to handle all input validation for the application.
    """

    @staticmethod
    def validate_audio_file(file_path: str):
        """
        Validates an uploaded audio file against the rules in config.py.

        This method checks for file existence, type, size, and duration.

        Args:
            file_path: The path to the uploaded audio file.

        Raises:
            ValidationError: If the file does not exist.
            InvalidFileType: If the file extension is not in the allowed list.
            FileSizeExceeded: If the file size is over the configured limit.
            FileLengthExceeded: If the audio duration is over the configured limit.
            ValidationError: If the audio file is corrupted or cannot be read.
        """
        logger.info(f"Initiating validation for file: {file_path}")

        # 1. Check for file existence
        if not os.path.exists(file_path):
            logger.error(f"Validation failed: File not found at {file_path}")
            raise ValidationError(f"File not found at path: {file_path}")

        # 2. Validate file type (extension)
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in config.ALLOWED_FILE_EXTENSIONS:
            logger.warning(
                f"Validation failed: Invalid file type '{ext}' for {file_path}"
            )
            raise InvalidFileType(
                f"Invalid file type. Allowed types are: "
                f"{', '.join(config.ALLOWED_FILE_EXTENSIONS)}"
            )

        # 3. Validate file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > config.MAX_FILE_SIZE_MB:
            logger.warning(
                f"Validation failed: File size {file_size_mb:.2f}MB exceeds "
                f"limit of {config.MAX_FILE_SIZE_MB}MB for {file_path}"
            )
            raise FileSizeExceeded(
                f"File size of {file_size_mb:.2f}MB exceeds the "
                f"{config.MAX_FILE_SIZE_MB}MB limit."
            )

        # 4. Validate file duration
        try:
            audio = AudioSegment.from_file(file_path)
            duration_mins = len(audio) / (1000 * 60)
            if duration_mins > config.MAX_FILE_LENGTH_MINS:
                logger.warning(
                    f"Validation failed: Duration {duration_mins:.2f} mins exceeds "
                    f"limit of {config.MAX_FILE_LENGTH_MINS} mins for {file_path}"
                )
                raise FileLengthExceeded(
                    f"Audio duration of {duration_mins:.2f} minutes exceeds the "
                    f"{config.MAX_FILE_LENGTH_MINS} minute limit."
                )
        except CouldntDecodeError:
            logger.error(f"Validation failed: Could not decode audio file {file_path}. "
                         "It may be corrupted or an unsupported format.")
            raise ValidationError(
                "Failed to read audio file. It may be corrupted or in an "
                "unsupported format despite the file extension."
            )

        logger.info(f"Validation successful for file: {file_path}")
