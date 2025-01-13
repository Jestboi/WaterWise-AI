import logging
import os
import requests
import time
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import traceback

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
        
        Args:
            model_name (str): Name of the Ollama model to use
            api_base (str, optional): Base URL for Ollama API
        """
        self.model_name = model_name
        self.api_base = api_base or os.getenv('OLLAMA_API_URL', 'http://localhost:11434')
        self.history = []  # Store user interactions and responses
        self._m = 0  # Internal metric counter
        
        # Validate model availability with fallback
        try:
            if not self._validate_model():
                # Attempt alternative model or fallback strategy
                alternative_models = ['llama2', 'mistral', 'phi']
                for alt_model in alternative_models:
                    logger.warning(f"Attempting fallback to alternative model: {alt_model}")
                    self.model_name = alt_model
                    if self._validate_model():
                        logger.info(f"Successfully switched to alternative model: {alt_model}")
                        break
                else:
                    # No alternative models worked
                    logger.critical("All model validation attempts failed")
                    self.model_name = None  # Indicate no valid model
        except Exception as e:
            logger.critical(f"Unexpected error during model initialization: {e}")
            self.model_name = None
    
    def _validate_model(self, max_retries=5):
        """
        Robust model validation with comprehensive error handling and diagnostics.
        
        Args:
            max_retries (int): Maximum number of validation attempts
        
        Returns:
            bool: Model validation status
        """
        import time
        import requests
        
        # Extended configuration for model validation
        MODEL_DOWNLOAD_TIMEOUT = 900  # 15-minute timeout for large model downloads
        BASE_WAIT_TIME = 10  # Base wait time between retries
        
        # Diagnostic logging of Ollama configuration
        logger.info(f"Validating model: {self.model_name}")
        logger.info(f"Ollama API Base URL: {self.api_base}")
        
        for attempt in range(max_retries):
            try:
                # Comprehensive server health check
                health_response = requests.get(
                    f'{self.api_base}/api/version', 
                    timeout=30
                )
                
                if health_response.status_code != 200:
                    logger.warning(f"Ollama server health check failed: {health_response.text}")
                    time.sleep(BASE_WAIT_TIME * (2 ** attempt))
                    continue
                
                # Log server version for diagnostics
                server_version = health_response.json().get('version', 'Unknown')
                logger.info(f"Ollama Server Version: {server_version}")
                
                # Check available models with extended timeout
                tags_response = requests.get(
                    f'{self.api_base}/api/tags', 
                    timeout=60
                )
                
                if tags_response.status_code != 200:
                    logger.warning(f"Failed to fetch model tags: {tags_response.text}")
                    time.sleep(BASE_WAIT_TIME * (2 ** attempt))
                    continue
                
                models = tags_response.json().get('models', [])
                model_names = [model.get('name', '') for model in models]
                
                # Detailed model diagnostics
                logger.info(f"Available models: {model_names}")
                
                # Check if exact model or partial match exists
                model_match = any(
                    self.model_name in name or name in self.model_name 
                    for name in model_names
                )
                
                if model_match:
                    logger.info(f"Model {self.model_name} is available")
                    return True
                
                # Attempt model pull with comprehensive parameters
                logger.warning(f"Model {self.model_name} not found. Attempting to pull...")
                
                pull_response = requests.post(
                    f'{self.api_base}/api/pull', 
                    json={
                        'name': self.model_name, 
                        'stream': False,
                        'insecure': False,
                        'timeout': MODEL_DOWNLOAD_TIMEOUT
                    },
                    timeout=MODEL_DOWNLOAD_TIMEOUT
                )
                
                # Detailed pull response handling
                if pull_response.status_code in [200, 201]:
                    logger.info(f"Successfully downloaded model: {self.model_name}")
                    
                    # Verify model after download
                    time.sleep(10)  # Extended pause for model registration
                    verify_response = requests.get(f'{self.api_base}/api/tags', timeout=30)
                    
                    if verify_response.status_code == 200:
                        verify_models = verify_response.json().get('models', [])
                        if any(self.model_name in model.get('name', '') for model in verify_models):
                            logger.info(f"Model {self.model_name} verified successfully")
                            return True
                
                logger.warning(f"Model download failed. Status: {pull_response.status_code}")
                time.sleep(BASE_WAIT_TIME * (2 ** attempt))
            
            except requests.Timeout as timeout_err:
                logger.error(f"Timeout during model validation: {timeout_err}")
            
            except requests.ConnectionError as conn_err:
                logger.error(f"Connection error during model validation: {conn_err}")
            
            except Exception as e:
                logger.critical(f"Unexpected error in model validation: {e}")
                logger.critical(traceback.format_exc())
        
        # Final failure state with comprehensive error report
        logger.error(f"Could not validate or download model {self.model_name} after {max_retries} attempts")
        return False

    def generate_response(self, user_input: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate a response for the given user input with enhanced error handling.
        
        Args:
            user_input (str): User's input query
        
        Returns:
            Tuple[Optional[str], Optional[str]]: Generated response and error message (if any)
        """
        # Comprehensive model availability check
        if not self.model_name:
            logger.critical("No valid model available for response generation")
            return None, "AI service is currently unavailable. Please try again later."
        
        # Retry mechanism for model revalidation
        if not self._validate_model(max_retries=2):
            logger.error(f"Failed to validate model {self.model_name}")
            return None, "Unable to load AI model. Service temporarily unavailable."
        
        # Input validation with enhanced logging
        if not user_input or not isinstance(user_input, str):
            logger.error(f"Invalid input type or empty input: {type(user_input)}")
            return None, "Invalid input. Please provide a valid question."
        
        # Trim and sanitize input with detailed logging
        original_length = len(user_input)
        user_input = user_input.strip()[:2000]  # Limit input length
        
        if len(user_input) != original_length:
            logger.info(f"Input truncated from {original_length} to {len(user_input)} characters")
        
        if not user_input:
            logger.warning("Input became empty after stripping")
            return None, "Please provide a non-empty question."
        
        # Circuit breaker mechanism with enhanced tracking
        max_errors = 5
        if not hasattr(self, '_error_tracking'):
            self._error_tracking = {
                'count': 0,
                'last_reset': datetime.now()
            }
        
        # Reset error count if more than an hour has passed
        current_time = datetime.now()
        if (current_time - self._error_tracking.get('last_reset', current_time)).total_seconds() > 3600:
            self._error_tracking['count'] = 0
            self._error_tracking['last_reset'] = current_time
        
        if self._error_tracking['count'] > max_errors:
            logger.critical(f"Circuit breaker activated. Consecutive errors: {self._error_tracking['count']}")
            return None, "Service is temporarily unavailable. Please try again later."
        
        # Retry mechanism with comprehensive error handling
        max_retries = 3
        base_timeout = 30  # Increased base timeout
        
        for attempt in range(max_retries):
            try:
                # Prepare system message with clear, specific instructions
                system_message = """You are an advanced water conservation expert AI specializing in Turkey's water resources. 
                Provide precise, actionable advice on water conservation. Use authoritative sources like DSI and TUIK. 
                Be concise, practical, and focus on sustainable water management strategies."""
                
                # Prepare payload with intelligent configuration
                payload = {
                    'model': self.model_name,
                    'prompt': f"{system_message}\n\nUser: {user_input}\nAssistant:",
                    'stream': False,
                    'options': {
                        'temperature': 0.5,  # Balanced temperature for consistent responses
                        'top_p': 0.9,  # Slightly higher top_p for more diverse responses
                        'num_ctx': 2048,  # Increased context window
                    }
                }
                
                # Detailed logging for traceability
                logger.info(f"Generating response (Attempt {attempt + 1}/{max_retries})")
                logger.debug(f"Payload: {payload}")
                
                # Send request with dynamic timeout and error tracking
                response = requests.post(
                    f'{self.api_base}/api/generate', 
                    json=payload,
                    timeout=base_timeout * (attempt + 1)  # Increasing timeout
                )
                
                # Comprehensive response handling
                if response.status_code == 200:
                    try:
                        result = response.json()
                        generated_text = result.get('response', '').strip()
                        
                        if not generated_text:
                            logger.warning("Empty response generated")
                            self._error_tracking['count'] += 1
                            return None, "Unable to generate a meaningful response."
                        
                        # Reset error tracking on successful response
                        self._error_tracking['count'] = 0
                        self._error_tracking['last_reset'] = current_time
                        
                        # Store conversation history with metadata
                        self.history.append({
                            'timestamp': current_time,
                            'user_input': user_input,
                            'bot_response': generated_text,
                            'model': self.model_name,
                            'attempt': attempt + 1
                        })
                        
                        return generated_text, None
                    
                    except ValueError as json_err:
                        logger.error(f"JSON parsing error: {json_err}")
                        self._error_tracking['count'] += 1
                        return None, "Error processing AI response"
            
                elif response.status_code in [500, 503]:
                    logger.error(f"Server error (Status {response.status_code}) on attempt {attempt + 1}: {response.text}")
                    self._error_tracking['count'] += 1
                    
                    # Attempt model recovery
                    if attempt < max_retries - 1:
                        try:
                            pull_response = requests.post(
                                f'{self.api_base}/api/pull', 
                                json={'name': self.model_name, 'stream': False},
                                timeout=30
                            )
                            logger.info(f"Model recovery attempt: {pull_response.text}")
                        except Exception as pull_error:
                            logger.error(f"Model recovery failed: {pull_error}")
                    
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
            
                else:
                    logger.error(f"Unexpected API response: {response.status_code} - {response.text}")
                    self._error_tracking['count'] += 1
                    return None, f"Service error: {response.status_code}"
        
            except requests.Timeout:
                logger.warning(f"Request timed out on attempt {attempt + 1}")
                self._error_tracking['count'] += 1
                
                if attempt == max_retries - 1:
                    return None, "Request timed out. Please try again later."
        
            except requests.ConnectionError as conn_err:
                logger.error(f"Connection error: {conn_err}")
                self._error_tracking['count'] += 1
                
                if attempt == max_retries - 1:
                    return None, "Unable to connect to the AI service."
        
            except Exception as unexpected_err:
                logger.critical(f"Unexpected error: {unexpected_err}")
                self._error_tracking['count'] += 1
                
                if attempt == max_retries - 1:
                    return None, "An unexpected error occurred. Please try again later."
    
        # Fallback if all attempts fail
        logger.error("All response generation attempts failed")
        return None, "Service is currently unavailable. Please try again later."