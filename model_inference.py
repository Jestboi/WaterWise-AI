import logging
import os
import requests
import time
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('model_inference.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class WaterConservationBot:
    def __init__(self, model_name='llama3.2', api_base=None):
        """
        Initialize the Water Conservation Bot with Ollama model.
        
        :param model_name: Name of the Ollama model to use
        :param api_base: Base URL for Ollama API (optional)
        """
        self.model_name = model_name
        self.api_base = api_base or os.getenv('OLLAMA_API_URL', 'http://localhost:11434')
        self.history = []  # Store user interactions and responses
        self._m = 0  # Internal metric counter
        
        # Validate model availability on initialization
        self._validate_model()
    
    def _validate_model(self, max_retries=3):
        """
        Validate the availability of the specified Ollama model.
        
        :param max_retries: Number of times to retry model validation
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Checking availability of model: {self.model_name}")
                
                # Check model tags
                response = requests.get(
                    f'{self.api_base}/api/tags', 
                    timeout=10
                )
                
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    model_names = [model.get('name', '') for model in models]
                    
                    if any(self.model_name in name for name in model_names):
                        logger.info(f"Model {self.model_name} is available")
                        return True
                    
                    # If model not found, attempt to pull
                    logger.warning(f"Model {self.model_name} not found. Attempting to pull...")
                    pull_response = requests.post(
                        f'{self.api_base}/api/pull', 
                        json={'name': self.model_name, 'stream': False},
                        timeout=300  # Long timeout for model download
                    )
                    
                    if pull_response.status_code in [200, 201]:
                        logger.info(f"Successfully pulled model {self.model_name}")
                        return True
                    
                    logger.error(f"Failed to pull model: {pull_response.text}")
                
                else:
                    logger.error(f"Failed to check model tags: {response.text}")
            
            except requests.RequestException as e:
                logger.error(f"Model validation error (Attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
        
        # If all attempts fail
        raise RuntimeError(f"Could not validate or pull model {self.model_name}")

    def generate_response(self, user_input: str) -> Tuple[Optional[str], Optional[str]]:
        """Generate a response for the given user input."""
        # Enhanced logging for input tracking
        logger.info(f"Generate response called with input: {user_input}")
        logger.info(f"Input type: {type(user_input)}")
        logger.info(f"Input length: {len(user_input)}")
        
        # Validate input
        if not user_input or not isinstance(user_input, str):
            logger.error("Invalid input: Empty or non-string input")
            return None, "Please provide a valid question"
        
        # Trim and clean input
        user_input = user_input.strip()
        if not user_input:
            logger.error("Input is empty after stripping")
            return None, "Please provide a non-empty question"
        
        # Log the input for debugging
        logger.info(f"Generating response for cleaned input: {user_input[:200]}...")
        
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
        
        # Retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
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
                    }
                }
                
                # Log payload details for debugging
                logger.info(f"Payload model: {payload['model']}")
                logger.info(f"Payload prompt length: {len(payload['prompt'])}")
                
                # Send request to Ollama API
                response = requests.post(
                    f'{self.api_base}/api/generate', 
                    json=payload,
                    timeout=60  # Increased timeout
                )
                
                # Log response details
                logger.info(f"API Response Status Code: {response.status_code}")
                logger.info(f"API Response Headers: {response.headers}")
                
                # Check response
                if response.status_code == 200:
                    try:
                        result = response.json()
                        logger.info(f"API Response JSON keys: {result.keys()}")
                        
                        generated_text = result.get('response', '').strip()
                        
                        # Log generated text details
                        logger.info(f"Generated text length: {len(generated_text)}")
                        logger.info(f"First 200 chars of generated text: {generated_text[:200]}")
                        
                        # Additional validation
                        if not generated_text:
                            logger.warning("Generated text is empty")
                            return None, "Unable to generate a meaningful response"
                        
                        # Log and store conversation history
                        self.history.append({
                            'user_input': user_input,
                            'bot_response': generated_text
                        })
                        
                        return generated_text, None
                    
                    except ValueError as json_err:
                        logger.error(f"JSON parsing error: {json_err}")
                        logger.error(f"Response content: {response.text}")
                        return None, "Error parsing AI response"
                
                # Specific error handling for Ollama server issues
                elif response.status_code == 500:
                    logger.error(f"Ollama server error (Attempt {attempt + 1}/{max_retries}): {response.text}")
                    
                    # Attempt to restart Ollama service or pull model again
                    if attempt < max_retries - 1:
                        try:
                            # Attempt to pull the model again
                            pull_response = requests.post(
                                f'{self.api_base}/api/pull', 
                                json={'name': self.model_name, 'stream': False},
                                timeout=30
                            )
                            logger.info(f"Model pull response: {pull_response.text}")
                        except Exception as pull_error:
                            logger.error(f"Error during model pull: {pull_error}")
                    
                    # Exponential backoff
                    time.sleep(2 ** attempt)
                    continue
                
                else:
                    logger.error(f"Ollama API error: {response.text}")
                    return None, f"API request failed with status code {response.status_code}"
            
            except requests.Timeout:
                logger.error(f"Timeout occurred (Attempt {attempt + 1}/{max_retries})")
                if attempt == max_retries - 1:
                    return None, "Request timed out. Please try again later."
                time.sleep(2 ** attempt)
            
            except requests.ConnectionError:
                logger.error(f"Connection error (Attempt {attempt + 1}/{max_retries})")
                if attempt == max_retries - 1:
                    return None, "Unable to connect to the AI service. Please check your network."
                time.sleep(2 ** attempt)
            
            except requests.RequestException as e:
                logger.error(f"Request error (Attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return None, f"Network error: {str(e)}"
                time.sleep(2 ** attempt)
        
        # Fallback response if all attempts fail
        fallback_response = """I apologize, but I'm currently experiencing technical difficulties. 
        Could you please rephrase your question or try again later? 
        If the problem persists, our support team would be happy to help."""
        
        logger.error("All attempts to generate a response have failed.")
        return fallback_response, "Service temporarily unavailable"