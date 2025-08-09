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
    UI-facing function to handle the entire processing of an uploaded audio file.
    """
    if audio_file_path is None:
        # This can happen on initial load, so we just return the initial state.
        return (
            gr.update(interactive=False), gr.update(interactive=False),
            gr.update(interactive=False), gr.update(interactive=False),
            gr.update(interactive=False), "<p>Please upload a file to begin.</p>", ""
        )
        
    try:
        logger.info(f"UI received file: {audio_file_path}")
        controller.process_audio_file(audio_file_path)
        success_message = "<p style='color:green;'>File processed successfully. Ready for analysis.</p>"
        return (
            gr.update(interactive=True), gr.update(interactive=True),
            gr.update(interactive=True), gr.update(interactive=True),
            gr.update(interactive=True), success_message, ""
        )
    except AppError as e:
        logger.error(f"UI caught an application error: {e}")
        error_message = f"<p style='color:red;'>Error: {e}</p>"
        return (
            gr.update(interactive=False), gr.update(interactive=False),
            gr.update(interactive=False), gr.update(interactive=False),
            gr.update(interactive=False), error_message, ""
        )
    finally:
        # Clean up the temporary file created by Gradio
        if audio_file_path and os.path.exists(audio_file_path):
            try:
                os.remove(audio_file_path)
                logger.info(f"Cleaned up temporary file: {audio_file_path}")
            except OSError as e:
                logger.error(f"Error removing temporary file {audio_file_path}: {e}")

# UI Handler Functions

def get_transcript_ui(controller):
    try:
        return controller.get_transcript()
    except AppError as e:
        logger.error(f"UI caught an application error during analysis: {e}")
        return f"Error: {e}"

def get_summary_ui(controller):
    try:
        return controller.get_summary()
    except AppError as e:
        logger.error(f"UI caught an application error during analysis: {e}")
        return f"Error: {e}"

def get_sentiment_ui(controller):
    try:
        return controller.get_sentiment()
    except AppError as e:
        logger.error(f"UI caught an application error during analysis: {e}")
        return f"Error: {e}"

def answer_question_ui(question, controller):
    try:
        return controller.answer_question(question)
    except AppError as e:
        logger.error(f"UI caught an application error during analysis: {e}")
        return f"Error: {e}"

# Gradio UI Definition

with gr.Blocks(theme=gr.themes.Soft(), title=config.APP_TITLE) as demo:
    controller_state = gr.State(value=create_controller)

    gr.Markdown(f"# {config.APP_TITLE}")
    gr.Markdown(config.APP_DESCRIPTION)

    with gr.Row():
        with gr.Column(scale=1):
            audio_input = gr.Audio(type="filepath", label="Upload Audio File")
            status_output = gr.Markdown(value="<p>Please upload a file to begin.</p>")
            
            with gr.Accordion("Analysis Actions", open=True):
                transcript_btn = gr.Button("Show Transcript", interactive=False)
                summarize_btn = gr.Button("Summarize", interactive=False)
                sentiment_btn = gr.Button("Analyze Sentiment", interactive=False)

            with gr.Accordion("Ask a Question", open=True):
                 question_input = gr.Textbox(label="Enter your question here", interactive=False)
                 ask_btn = gr.Button("Get Answer", interactive=False)

        with gr.Column(scale=2):
            main_output = gr.Textbox(label="Results", lines=20, interactive=False, show_copy_button=True)

    # Wire up the components

    audio_input.upload(
        fn=process_audio_file,
        inputs=[audio_input, controller_state],
        outputs=[
            transcript_btn, summarize_btn, sentiment_btn, 
            question_input, ask_btn, status_output, main_output
        ]
    )

    transcript_btn.click(
        fn=get_transcript_ui,
        inputs=[controller_state],
        outputs=[main_output]
    )
    summarize_btn.click(
        fn=get_summary_ui,
        inputs=[controller_state],
        outputs=[main_output]
    )
    sentiment_btn.click(
        fn=get_sentiment_ui,
        inputs=[controller_state],
        outputs=[main_output]
    )
    ask_btn.click(
        fn=answer_question_ui,
        inputs=[question_input, controller_state],
        outputs=[main_output]
    )

if __name__ == "__main__":
    logger.info("Starting Gradio application...")
    demo.launch(
        share=True,
        show_error=True,
    )
