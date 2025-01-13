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
        """Generate a response for the given user input with enhanced error handling."""
        # Comprehensive input validation
        if not user_input or not isinstance(user_input, str):
            logger.error(f"Invalid input received: {user_input}")
            return None, "Invalid input. Please provide a valid question."
        
        # Trim and sanitize input
        user_input = user_input.strip()[:2000]  # Limit input length
        
        if not user_input:
            logger.warning("Empty input after stripping")
            return None, "Please provide a non-empty question."
        
        # Circuit breaker tracking
        if hasattr(self, '_error_count') and self._error_count > 5:
            logger.critical(f"Circuit breaker activated. Too many consecutive errors: {self._error_count}")
            return None, "Service is temporarily unavailable. Please try again later."
        
        # Retry mechanism with exponential backoff
        max_retries = 2
        base_timeout = 10  # Base timeout in seconds
        
        for attempt in range(max_retries):
            try:
                # Prepare system message with clear instructions
                system_message = """You are a highly knowledgeable water conservation expert AI focused on Turkey. 
                Provide accurate, concise, and actionable answers about water conservation. 
                Use information from DSI and TUIK when possible. Be direct and practical."""
                
                # Prepare payload with reduced complexity
                payload = {
                    'model': self.model_name,
                    'prompt': f"{system_message}\n\nUser: {user_input}\nAssistant:",
                    'stream': False,
                    'options': {
                        'temperature': 0.6,  # Slightly reduced temperature for more consistent responses
                        'top_p': 0.8,
                    }
                }
                
                # Log payload for debugging
                logger.info(f"Payload for attempt {attempt + 1}: {payload}")
                
                # Send request with dynamic timeout
                response = requests.post(
                    f'{self.api_base}/api/generate', 
                    json=payload,
                    timeout=base_timeout * (attempt + 1)  # Increasing timeout
                )
                
                # Log response details
                logger.info(f"API Response Status: {response.status_code}")
                
                # Handle different response scenarios
                if response.status_code == 200:
                    try:
                        result = response.json()
                        generated_text = result.get('response', '').strip()
                        
                        if not generated_text:
                            logger.warning("Empty response generated")
                            return None, "Unable to generate a meaningful response."
                        
                        # Reset error count on successful response
                        if hasattr(self, '_error_count'):
                            self._error_count = 0
                        
                        # Store conversation history
                        self.history.append({
                            'user_input': user_input,
                            'bot_response': generated_text
                        })
                        
                        return generated_text, None
                    
                    except ValueError as json_err:
                        logger.error(f"JSON parsing error: {json_err}")
                        return None, "Error processing AI response"
                
                elif response.status_code == 500:
                    logger.error(f"Server error on attempt {attempt + 1}: {response.text}")
                    
                    # Increment error tracking
                    if not hasattr(self, '_error_count'):
                        self._error_count = 0
                    self._error_count += 1
                    
                    # Optional: Attempt to pull model again
                    if attempt < max_retries - 1:
                        try:
                            pull_response = requests.post(
                                f'{self.api_base}/api/pull', 
                                json={'name': self.model_name, 'stream': False},
                                timeout=30
                            )
                            logger.info(f"Model pull response: {pull_response.text}")
                        except Exception as pull_error:
                            logger.error(f"Model pull error: {pull_error}")
                    
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                
                else:
                    logger.error(f"Unexpected API response: {response.status_code} - {response.text}")
                    return None, f"Service error: {response.status_code}"
            
            except requests.Timeout:
                logger.warning(f"Request timed out on attempt {attempt + 1}")
                
                # Increment error tracking
                if not hasattr(self, '_error_count'):
                    self._error_count = 0
                self._error_count += 1
                
                if attempt == max_retries - 1:
                    return None, "Request timed out. Please try again later."
            
            except requests.ConnectionError:
                logger.error("Connection error occurred")
                
                # Increment error tracking
                if not hasattr(self, '_error_count'):
                    self._error_count = 0
                self._error_count += 1
                
                if attempt == max_retries - 1:
                    return None, "Unable to connect to AI service"
            
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                
                # Increment error tracking
                if not hasattr(self, '_error_count'):
                    self._error_count = 0
                self._error_count += 1
                
                if attempt == max_retries - 1:
                    return None, "An unexpected error occurred"
        
        # Fallback response if all attempts fail
        logger.critical("All response generation attempts failed")
        return "I apologize, but I'm currently unable to process your request. Please try again later.", None