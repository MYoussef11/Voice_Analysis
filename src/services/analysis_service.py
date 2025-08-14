import ollama
from openai import OpenAI, OpenAIError
from src import config
from src.utils.exceptions import AnalysisError, IrrelevantQuestionError
from src.logging_config import logger


class AnalysisService:
    """
    A service class for performing text analysis tasks.
    It uses Ollama for local analysis and the OpenAI API for remote analysis.
    """

    def _analyze_local(self, prompt: str) -> str:
        """
        Generates a response by calling the local Ollama server using the host
        address defined in the application's configuration.
        """

        # Read the configured host from config.py
        ollama_host = config.OLLAMA_HOST
        
        try:
            # Initialize the Ollama client with the determined host
            client = ollama.Client(host=f"http://{ollama_host}:11434")
            logger.info(f"Sending analysis request to Ollama server at {ollama_host}.")
            
            response = client.generate(
                model=config.OLLAMA_MODEL,
                prompt=prompt
            )
            
            logger.info("Ollama analysis successful.")
            return response['response'].strip()

        except ollama.ResponseError as e:
            logger.error(f"Ollama API error: {e.error}", exc_info=True)
            raise AnalysisError(f"An error occurred with the Ollama API: {e.error}")
        except Exception as e:
            # Catch other potential issues like connection problems
            logger.error(f"Error during Ollama request: {e}", exc_info=True)
            raise AnalysisError("An unexpected error occurred while communicating with the Ollama server.")

    def _analyze_openai(self, prompt: str) -> str:
        """
        Generates a response using the OpenAI API.
        """
        if not config.OPENAI_API_KEY:
            logger.error("OpenAI API key not found for analysis.")
            raise AnalysisError("OpenAI API key is not configured.")
        
        try:
            logger.info("Sending analysis request to OpenAI.")
            client = OpenAI(api_key=config.OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model=config.OPENAI_ANALYSIS_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.choices[0].message.content
            logger.info("OpenAI analysis successful.")
            return content.strip()
        except OpenAIError as e:
            logger.error(f"OpenAI API error during analysis: {e.response.text}", exc_info=True)
            raise AnalysisError(f"An OpenAI API error occurred: {e.response.status_code}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during OpenAI analysis: {e}", exc_info=True)
            raise AnalysisError("An unexpected error occurred while using the OpenAI API.")

    def _analyze(self, prompt: str) -> str:
        """
        Private dispatcher method to route analysis to the correct provider.
        """
        provider = config.MODEL_PROVIDER.lower()
        if provider == 'local':
            return self._analyze_local(prompt)
        elif provider == 'openai':
            return self._analyze_openai(prompt)
        else:
            logger.error(f"Invalid MODEL_PROVIDER configured: {config.MODEL_PROVIDER}")
            raise ValueError(f"Invalid model provider '{config.MODEL_PROVIDER}' specified in config.")

    def summarize(self, text: str) -> str:
        """
        Generates a summary of the provided text.
        """
        logger.info("Summarization task requested.")
        prompt = f"""
        Provide a concise summary of the following text. 
        Focus on the key points and main conclusions.

        Text:
        ---
        {text}
        ---
        Summary:
        """
        return self._analyze(prompt)

    def get_sentiment(self, text: str) -> str:
        """
        Performs sentiment analysis on the provided text.
        """
        logger.info("Sentiment analysis task requested.")
        prompt = f"""
        Analyze the sentiment of the following text.
        Your response must have two parts:
        1.  **Sentiment:** Classify the sentiment as Positive, Negative, or Neutral.
        2.  **Justification:** Briefly explain why you chose that sentiment, referencing key words or phrases from the text.

        Format your response clearly using Markdown.

        Text:
        ---
        {text}
        ---
        Sentiment:
        """
        return self._analyze(prompt)

    def answer_question(self, text: str, question: str, chat_history: list) -> str:
        """
        Answers a question based on the provided text.
        """
        logger.info(f"Q&A task requested for question: '{question}'")
        # Format the chat history for the prompt
        formatted_history = "\n".join([f"User: {q}\nAssistant: {a}" for q, a in chat_history])
        
        prompt = f"""
        You are a machine. You are a Q&A engine that answers questions about a document.
        You MUST follow these rules strictly:
        1. Use the "Conversation History" to understand the user's question, especially for follow-ups.
        2. Find the answer to the user's "New User Question" using ONLY the "Document Transcript".
        3. If the answer is not in the transcript, you MUST ONLY respond with the exact phrase: 'That information is not available in the provided document.'
        4. Do not apologize. Do not explain your reasoning. Do not add any other words.

        ---
        **DOCUMENT TRANSCRIPT:**
        {text}
        ---
        **CONVERSATION HISTORY:**
        {formatted_history}
        ---
        **NEW USER QUESTION:**
        {question}
        """
        
        response = self._analyze(prompt)
        
        # Check for our custom error signal from the LLM
        if "ERROR: The answer to this question cannot be found" in response:
            logger.warning(f"Model indicated question '{question}' is unanswerable from text.")
            raise IrrelevantQuestionError(
                "The question could not be answered based on the provided audio content."
            )
            
        return response
