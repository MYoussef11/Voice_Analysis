# Voice Analysis Toolkit

## Project Overview

Voice Analysis Toolkit is a powerful, locally-hosted web application designed to transform spoken audio into structured, actionable intelligence. By leveraging state-of-the-art voice-to-text and large language models, this tool provides a private and efficient way to transcribe, summarize, analyze, and query audio content.

The entire process runs on your own machine, ensuring that your sensitive conversations, meetings, and recordings remain completely confidential.

## Key Features

*   **Automatic Transcription:** Upload an audio file (MP3, WAV, M4A, etc.) and get a full text transcript.
*   **On-Demand Analysis:** Once transcribed, perform a suite of actions on the content:
    *   **Full Transcript:** View the complete, time-stamped text.
    *   **Concise Summaries:** Get the key points and takeaways in seconds.
    *   **Sentiment Analysis:** Understand the emotional tone of the conversation.
    *   **Intelligent Q&A:** Ask specific questions about the content ("What was the final decision on Project X?") and get direct answers.
*   **100% Private:** All processing happens locally. Your files and data never leave your computer.
*   **Simple Web Interface:** An intuitive interface built with Gradio makes the tool accessible to everyone.

## Who is this for?

This toolkit is designed for professionals who regularly work with audio and need to quickly recall or analyze information. For example:

*   **Project Managers & Team Leads:** Quickly review action items and decisions from recorded meetings.
*   **Journalists & Researchers:** Transcribe interviews and easily search for key quotes.
*   **Sales Professionals & Customer Support:** Analyze call sentiment and summarize client needs.
*   **Students & Academics:** Transcribe lectures and seminars for easier studying and citation.

Essentially, if you've ever wished you could "Ctrl+F" your own conversations, this tool is for you.

## Setup Instructions

This project uses Conda for environment management to ensure consistency.

**1. Clone the Repository:**
```bash```
git clone https://github.com/MYoussef11/Voice_Analysis.git
cd voice-analysis-project 

**2. Create and Activate the Conda Environment:**
```bash```
conda create -n voice-app python=3.10 -y
conda activate voice-app

**3. Install Dependencies:**
```bash```
pip install -r requirements.txt

⚠️Note on PyTorch: The requirements file will install the CPU version of PyTorch. If you have a compatible NVIDIA GPU for significantly faster performance, please follow the official PyTorch instructions to install the correct CUDA-enabled version: https://pytorch.org/get-started/locally/

**4. Set Up Environment Variables:**
This step is only necessary if you plan to use the OpenAI API instead of local models.
cp .env.example .env

**5. How to Use:**
With your conda environment active:

    1. Navigate to the src directory:
    ```bash```
    cd src

    2.Run the application:
    ```bash```
    python app.py

    3.Open your web browser and go to the local URL provided by Gradio (usually http://127.0.0.1:7860)

# You can now upload your audio files and begin analysis.