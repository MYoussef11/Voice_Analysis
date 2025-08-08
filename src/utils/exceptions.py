class AppError(Exception):
    """Base exception class for the application."""
    pass

class ValidationError(AppError):
    """Custom exception for data validation errors."""
    pass

class InvalidFileType(ValidationError):
    """Raised when the uploaded file type is not allowed."""
    pass

class FileSizeExceeded(ValidationError):
    """Raised when the uploaded file is larger than the allowed limit."""
    pass

class FileLengthExceeded(ValidationError):
    """Raised when the uploaded audio file's duration is longer than the allowed limit."""
    pass

class TranscriptionError(AppError):
    """Raised when there is an error during the transcription process."""
    pass

class AnalysisError(AppError):
    """Raised when there is an error during the text analysis process."""
    pass

class IrrelevantQuestionError(AnalysisError):
    """Raised when a user's question is not related to the provided text."""
    pass
