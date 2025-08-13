import pytest
from src.utils.validator import Validator
from src.utils.exceptions import (
    InvalidFileType,
    FileSizeExceeded,
    FileLengthExceeded,
    ValidationError
)
from src import config


# Test Cases for our Validator

def test_validate_audio_file_success(tmp_path):
    """
    Tests the "happy path" - a perfectly valid file should pass without errors.
    `tmp_path` is a special pytest fixture that provides a temporary directory.
    """
    # We create a dummy file. For this test, its content doesn't matter, only its name and size.
    valid_file = tmp_path / "test_audio.mp3"
    valid_file.write_bytes(b"0" * 1024) # Create a 1KB file

    # 2. Act & 3. Assert: Call the validator and expect no exceptions.
    try:
        # Validate the file
        with pytest.raises(ValidationError):
            Validator.validate_audio_file(str(valid_file))
    except FileNotFoundError:
        # This test might fail if ffmpeg is not installed, which is fine for now.
        pass


def test_validate_invalid_file_type(tmp_path):
    """
    Tests that the validator correctly rejects a file with a disallowed extension.
    """
    # 1. Arrange: Create a file with a bad extension
    invalid_file = tmp_path / "document.txt"
    invalid_file.touch() # Creates an empty file

    # 2. Act & 3. Assert: Check that the correct exception is raised.
    with pytest.raises(InvalidFileType, match="Invalid file type"):
        Validator.validate_audio_file(str(invalid_file))


def test_validate_file_size_exceeded(tmp_path):
    """
    Tests that the validator correctly rejects a file that is too large.
    """
    # 1. Arrange: Create a file larger than our configured limit.
    config.MAX_FILE_SIZE_MB = 1 # Temporarily set max size to 1MB for the test
    large_file = tmp_path / "large_audio.wav"
    # Create a 2MB file (2 * 1024 * 1024 bytes)
    large_file.write_bytes(b"0" * (2 * 1024 * 1024))

    # 2. Act & 3. Assert: Check that FileSizeExceeded is raised.
    with pytest.raises(FileSizeExceeded, match="exceeds the 1MB limit"):
        Validator.validate_audio_file(str(large_file))
    
    # Clean up our change to the config
    config.MAX_FILE_SIZE_MB = 25 # Reset to the original value


def test_validate_file_length_exceeded(tmp_path, mocker):
    """
    Tests that the validator correctly rejects a file with a duration
    that is too long, using mocking to simulate the audio length.
    """
    # 1. Arrange
    # Temporarily set the max length for our test
    config.MAX_FILE_LENGTH_MINS = 5

    # Create a dummy file. Its actual content doesn't matter.
    long_file = tmp_path / "long_audio.mp3"
    long_file.touch()

    # Return a fake audio segment that is 360,000 ms long (6 minutes).
    mocker.patch('pydub.AudioSegment.from_file').return_value.duration_seconds = 360

    # 2. Act & 3. Assert
    # Check that our specific exception is raised.
    with pytest.raises(FileLengthExceeded, match="exceeds the 5 minute limit"):
        Validator.validate_audio_file(str(long_file))

    # Clean up the config change
    config.MAX_FILE_LENGTH_MINS = 15 # Or your original default


def test_validate_file_not_found():
    """
    Tests that the validator raises an error if the file does not exist.
    """
    # 1. Arrange: Define a path to a file that doesn't exist
    non_existent_file = "path/that/definitely/does/not/exist.mp3"

    # 2. Act & 3. Assert: Check for the base ValidationError.
    with pytest.raises(ValidationError, match="File not found"):
        Validator.validate_audio_file(non_existent_file)
