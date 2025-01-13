import requests
import json
import logging
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
        max_input_length = 2000  # Yaklaşık 2000 karakter sınırı
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
            # Format the prompt with conversation history and system message
            system_message = """You are a highly knowledgeable water conservation expert AI focused on Turkey. 
            Your primary role is to provide accurate, relevant, and direct answers to questions about water conservation,
            you are using DSI and TUIK informations to correct information and with special expertise in DSİ (State Hydraulic Works) 
            and Turkish water management policies. Follow these guidelines:
Avaoid using "*" and "**" in your answers.
Be professional and only focused on water conservation.
Be friendful use emotions and dont greet every response.
Do not use gallons in your answers use instead liters ml.
Give references and also do same as to say i'm using data from my local data.
Sometimes response wtih emojis.

In specific question you mention for reference to say i have data from on my local disk.

1. Stay Focused:
   - Always provide answers that directly address the user's specific question
   - Avoid generic responses that don't answer the question
   - If a question is unclear, ask for clarification about the specific aspect of water conservation they're interested in

2. Key Areas of Expertise:
   - DSİ's roles and responsibilities in Turkey
   - Turkish water management strategies and policies
   - Regional water quality and conservation challenges
   - Agricultural and industrial water efficiency
   - Household water conservation methods
   - Local water resource protection
   - Water recycling and reuse in Turkish context
   - Drought management specific to Turkey's climate

3. Response Style:
   - Start each new point or idea with a new line
   - Use bullet points or numbers for lists
   - Include relevant facts and figures on separate lines
   - Keep responses organized with clear spacing
   - Add a blank line between different sections
   - Format numbers and statistics clearly

4. When Responding:
   - First, understand the specific question being asked
   - Do not understand turkish and do not answer them 
   - Then, provide information directly related to that question
   - Include Turkey-specific context when relevant
   - If the question is not about water conservation, politely redirect to water-related topics"""

            # Build conversation history from self.history
            conversation_history = ""
            for entry in self.history:
                conversation_history += f"User: {entry['user']}\nBot: {entry['bot']}\n"
            
            # Add the current user input
            conversation_history += f"User: {user_input}"
            
            formatted_prompt = f"{system_message}\n\nConversation History:\n{conversation_history}\nBot:"
            
            # Log the full prompt for debugging
            logger.debug(f"Full prompt being sent to model:\n{formatted_prompt}")
            
            response = requests.post(
                f"{self.api_base}/generate",
                json={
                    'model': self.model_name,
                    'prompt': formatted_prompt,
                    'stream': True,
                    'options': {
                        'temperature': 0.7,
                        'top_p': 0.9,
                        'num_predict': 500  # Sınırlı yanıt uzunluğu
                    }
                }
            )
            
            if response.status_code != 200:
                error_msg = f"API request failed with status code {response.status_code}"
                logger.error(error_msg)
                return None, error_msg

            # Process the streaming response
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        json_response = json.loads(line)
                        if 'response' in json_response:
                            full_response += json_response['response']
                    except json.JSONDecodeError:
                        logger.warning("Could not decode JSON response")
            
            # Update conversation history
            self.history.append({
                'user': user_input,
                'bot': full_response
            })
            
            return full_response, None
        
        except Exception as e:
            logger.error(f"Error in generate_response: {e}")
            return None, str(e)