from enum import Enum
import os
import time
import requests
import dotenv
import logging

dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

class GeminiStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class llm_request:
    def __init__(self, prompt: str):
        self.prompt = prompt
        self.response: str = ""
        self.status: GeminiStatus = GeminiStatus.PENDING
        self.retries: int = 0
        self.MAX_RETRIES: int = 5  # Maximum number of retries for LLM requests

    def get_llm_response(self):
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

        logger.info(f"Preparing LLM request using Gemini API")
        
        api_key = GEMINI_API_KEY
        fallback_api_urls = [
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}",
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={api_key}",
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        ]
        
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": self.prompt
                        }
                    ]
                }
            ],
        }
        
        def try_llms():
            for url in fallback_api_urls:
                try:
                    logger.info(f"Trying API endpoint: {url.split('models/')[1].split(':')[0]}")
                    logger.debug(f"Request URL: {url}")
                    
                    response = requests.post(url, headers=headers, json=data)
                    logger.info(f"Received response with status code: {response.status_code}")
                    
                    if response.status_code == 200:
                        logger.debug(f"Response JSON: {response.json()}")
                        return response.json()
                    else:
                        logger.warning(f"Error with model: {response.status_code} - {response.text}")
                except Exception as e:
                    logger.error(f"Exception occurred: {str(e)}")
        
        while self.status != GeminiStatus.COMPLETED:
            response_json = try_llms()
            if response_json:
                self.response = response_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                if self.response.startswith("```json"):
                    self.response = self.response[7:-3].strip()
                if self.response.endswith("```"):
                    self.response = self.response[:-3].strip()
                if self.response:
                    self.status = GeminiStatus.COMPLETED
                    logger.info("LLM response successfully retrieved")
                    return self.response
            else:
                self.status = GeminiStatus.FAILED
                logger.error("Failed to retrieve LLM response from all fallback models. Sleeping before retrying...")
                time.sleep(5)
                logger.info("Retrying after the sleep...")
                self.status = GeminiStatus.PENDING
                self.retries += 1
                if self.retries >= self.MAX_RETRIES:
                    logger.error("Maximum retries reached. Exiting with failure.")
                    raise ValueError("Failed to get response from any Gemini model after maximum retries")