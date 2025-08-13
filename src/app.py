import gradio as gr
import os
from src.controllers.processing_controller import ProcessingController
from src.utils.exceptions import AppError
from src.logging_config import logger
from src import config


def create_controller():
    """Factory function to create a new controller instance."""
    return ProcessingController()

def process_audio_file(audio_file_path, controller):
    """
    Handles the primary audio processing workflow when a user uploads a file.
    """
    # Define the updates for a failed state (all components disabled)
    fail_updates = (
        gr.update(), gr.update(interactive=False), gr.update(interactive=False),
        gr.update(interactive=False), gr.update(interactive=False),
        gr.update(interactive=False), "<p>Please upload a file to begin.</p>", []
    )
    # Define the updates for a successful state (all components enabled)
    success_updates = (
        gr.update(), gr.update(interactive=True), gr.update(interactive=True),
        gr.update(interactive=True), gr.update(interactive=True),
        gr.update(interactive=True), "<p style='color:green;'>File processed successfully. Ready for analysis.</p>", []
    )

    if audio_file_path is None:
        return fail_updates
        
    try:
        logger.info(f"UI received file: {audio_file_path}")
        controller.process_audio_file(audio_file_path)
        return success_updates
    except AppError as e:
        logger.error(f"UI caught an application error: {e}")
        # Return a failure state but with a specific error message for the user.
        error_return = list(fail_updates)
        error_return[6] = f"<p style='color:red;'>Error: {e}</p>"
        return tuple(error_return)
    finally:
        # Ensure temporary files created by Gradio are always cleaned up.
        if audio_file_path and os.path.exists(audio_file_path):
            try:
                os.remove(audio_file_path)
                logger.info(f"Cleaned up temporary file: {audio_file_path}")
            except OSError as e:
                logger.error(f"Error removing temporary file {audio_file_path}: {e}")

def handle_question(question, controller):
    """
    Manages the conversational Q&A flow. It takes the user's question, gets the
    model's response via the controller, and returns the updated chat history.
    """
    if not question.strip():
        # Do not process empty questions, just return the current state.
        return controller.chat_history, ""
    try:
        # The controller manages appending the new Q&A turn to its internal history.
        controller.answer_question(question)
        # Return the full, updated history and a blank string to clear the input box.
        return controller.chat_history, ""
    except AppError as e:
        logger.error(f"UI caught an application error during Q&A: {e}")
        # On error, create a temporary history to show the error without saving it to the permanent chat log.
        temp_history = controller.chat_history + [[question, f"Error: {e}"]]
        return temp_history, question

def handle_transcript(controller, chat_history):
    """Appends the full transcript to the current chat display."""
    chat_history.append([None, controller.get_transcript()])
    return chat_history

def handle_summary(controller, chat_history):
    """Appends a generated summary to the current chat display."""
    chat_history.append([None, controller.get_summary()])
    return chat_history

def handle_sentiment(controller, chat_history):
    """Appends a sentiment analysis to the current chat display."""
    chat_history.append([None, controller.get_sentiment()])
    return chat_history

#  Gradio UI Definition 
with gr.Blocks(theme=gr.themes.Default(), css="footer {visibility: hidden}", title=config.APP_TITLE) as demo:
    # A session-specific state object to hold a unique controller instance for each user.
    controller_state = gr.State(value=create_controller)

    # Main layout starts here.
    gr.Markdown(f"# 🗣️ {config.APP_TITLE}")
    gr.Markdown(config.APP_DESCRIPTION)

    with gr.Row(equal_height=True):
        # Left column for inputs and actions
        with gr.Column(scale=1):
            audio_input = gr.Audio(type="filepath", label="Upload Audio File")
            status_output = gr.Markdown(value="<p>Please upload a file to begin.</p>")
            
            with gr.Accordion("Analysis Actions", open=True):
                transcript_btn = gr.Button("Show Full Transcript", interactive=False)
                summarize_btn = gr.Button("Generate Summary", interactive=False)
                sentiment_btn = gr.Button("Analyze Sentiment", interactive=False)
        
        # Right column for chatbot interaction
        with gr.Column(scale=2):
            chatbot_ui = gr.Chatbot(label="Chatbot", height=500, show_copy_button=True)
            with gr.Row():
                question_input = gr.Textbox(
                    show_label=False,
                    placeholder="Type your question here...",
                    interactive=False,
                    scale=4
                )
                submit_btn = gr.Button(
                    value="Submit", 
                    interactive=False, 
                    variant="primary",
                    scale=1
                )

    # Defines how UI components react to user actions.
    # Handle the audio file upload and processing.
    audio_input.upload(
        fn=process_audio_file,
        inputs=[audio_input, controller_state],
        outputs=[
            audio_input, transcript_btn, summarize_btn, sentiment_btn, 
            question_input, submit_btn, status_output, chatbot_ui
        ]
    )

    #  Handle the analysis actions.
    transcript_btn.click(fn=handle_transcript, inputs=[controller_state, chatbot_ui], outputs=[chatbot_ui])
    summarize_btn.click(fn=handle_summary, inputs=[controller_state, chatbot_ui], outputs=[chatbot_ui])
    sentiment_btn.click(fn=handle_sentiment, inputs=[controller_state, chatbot_ui], outputs=[chatbot_ui])

    # Handle the question submission.
    question_input.submit(fn=handle_question, inputs=[question_input, controller_state], outputs=[chatbot_ui, question_input])
    submit_btn.click(fn=handle_question, inputs=[question_input, controller_state], outputs=[chatbot_ui, question_input])

if __name__ == "__main__":
    logger.info("Starting Gradio application...")
    demo.launch(
        #share=True
    )
