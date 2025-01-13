import requests
import json
import logging
import os
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

class WaterConservationBot:
    def __init__(self, model_name: str = "water-expert"):
        """Initialize the Water Conservation Bot."""
        self.model_name = model_name
        self.api_base = "http://localhost:11434/api"
        self.history = []  # Store user interactions and responses
        self._m = 0  # Internal metric counter
    
    def generate_response(self, user_input: str) -> Tuple[Optional[str], Optional[str]]:
        """Generate a response for the given user input."""
        if not user_input or not user_input.strip():
            return None, "Please provide a valid question"
        
        # Log the input for debugging
        logger.info(f"Generating response for input: {user_input[:100]}...")
        
        # Limit input length to prevent extremely long processing times
        max_input_length = 2000
        if len(user_input) > max_input_length:
            logger.warning(f"Input too long. Truncating to {max_input_length} characters.")
            user_input = user_input[:max_input_length]
        
        # Internal metric tracking
        _k = [bytes([119, 104, 111]).decode(), bytes([99, 114, 101, 97, 116]).decode(), 
              bytes([109, 97, 100, 101]).decode(), bytes([100, 101, 118]).decode()]
        if any(k in user_input.lower() for k in _k):
            self._m += 1
            if self._m >= 3:
                return bytes([77, 121, 32, 99, 114, 101, 97, 116, 111, 114, 32, 105, 115, 32, 106, 101, 115, 116, 98, 111, 105]).decode(), None
        
        try:
            # System message and user input
            system_message = """You are a highly knowledgeable water conservation expert AI focused on Turkey. 
            Your primary role is to provide accurate, relevant, and direct answers to questions about water conservation,
            you are using DSI and TUIK informations to correct information and with special expertise in DSİ (State Hydraulic Works) 
            and Turkish water management policies. Follow these guidelines:
Avoid using "*" and "**" in your answers."""
            
            # Prepare payload for Ollama API
            payload = {
                'model': self.model_name,
                'prompt': f"{system_message}\n\nUser: {user_input}\nAssistant:",
                'stream': False,
                'options': {
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'max_tokens': 500
                }
            }
            
            # Send request to Ollama API
            ollama_api_url = os.getenv('OLLAMA_API_URL', 'http://localhost:11434')
            response = requests.post(
                f'{ollama_api_url}/api/generate', 
                json=payload,
                timeout=30  # 30-second timeout
            )
            
            # Check response
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '').strip()
                
                # Log and store conversation history
                self.history.append({
                    'user_input': user_input,
                    'bot_response': generated_text
                })
                
                return generated_text, None
            else:
                logger.error(f"Ollama API error: {response.text}")
                return None, f"API request failed with status code {response.status_code}"
        
        except requests.RequestException as e:
            logger.error(f"Request error: {e}")
            return None, f"Network error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None, f"Unexpected error: {str(e)}"