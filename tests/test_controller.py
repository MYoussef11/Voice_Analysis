import pytest
from src.controllers.processing_controller import ProcessingController
from src.utils.exceptions import ValidationError, AppError


# This ensures tests are isolated and don't interfere with each other.
@pytest.fixture
def controller():
    return ProcessingController()

def test_process_audio_file_success(controller, mocker):
    """
    Tests the main success path of the controller.
    We will mock the validator and transcription service to simulate a successful run.
    """
    # 1. Arrange
    fake_file_path = "path/to/fake/audio.mp3"
    expected_transcript = "This is a test transcript."

    # Mock the dependencies:
    # Replace the Validator's method with a mock that does nothing.
    mocker.patch("src.utils.validator.Validator.validate_audio_file")
    # Replace the TranscriptionService's method with a mock that returns our expected text.
    mocker.patch(
        "src.services.transcription_service.TranscriptionService.transcribe",
        return_value=expected_transcript
    )

    # 2. Act: Run the method we are testing.
    controller.process_audio_file(fake_file_path)

    # 3. Assert: Check that the controller's internal state (the transcript) was set correctly.
    assert controller.transcript == expected_transcript


def test_process_audio_file_validation_fails(controller, mocker):
    """
    Tests that if the validator raises an error, the controller catches it
    and the process stops (i.e., transcription is never called).
    """
    # 1. Arrange
    fake_file_path = "path/to/bad/file.txt"

    # Mock the Validator to raise an error when called.
    mocker.patch(
        "src.utils.validator.Validator.validate_audio_file",
        side_effect=ValidationError("Bad file!")
    )
    # We also create a "spy" on the transcribe method to make sure it's NOT called.
    transcribe_spy = mocker.spy(controller.transcription_service, "transcribe")

    # 2. Act & 3. Assert
    # Check that the controller correctly propagates the validation error.
    with pytest.raises(ValidationError, match="Bad file!"):
        controller.process_audio_file(fake_file_path)

    # Assert that transcription was never attempted.
    assert transcribe_spy.call_count == 0
    # Assert that the controller's transcript state remains empty.
    assert controller.transcript is None


def test_get_summary_success(controller, mocker):
    """
    Tests the summary functionality after a file has been successfully processed.
    """
    # 1. Arrange: First, we need to get the controller into a "processed" state.
    controller.transcript = "This is a test transcript." # Set the state directly.
    expected_summary = "This is a summary."

    # Mock the AnalysisService to return our fake summary.
    mocker.patch(
        "src.services.analysis_service.AnalysisService.summarize",
        return_value=expected_summary
    )

    # 2. Act
    result = controller.get_summary()

    # 3. Assert
    assert result == expected_summary


def test_get_summary_before_processing_fails(controller):
    """
    Tests the guard condition: an error should be raised if we request a summary
    before a file has been processed.
    """
    # 1. Arrange
    # The controller is in its initial state, `controller.transcript` is None.

    # 2. Act & 3. Assert
    # Check that the specific AppError is raised.
    with pytest.raises(AppError, match="Please process an audio file before requesting analysis."):
        controller.get_summary()
