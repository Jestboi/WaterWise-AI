import json
import requests
import time
import os
import logging
from tqdm import tqdm
from torch.utils.tensorboard import SummaryWriter
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # Increase backoff factor
REQUEST_TIMEOUT = 60  # Increase timeout

def create_session():
    """Create a requests session with retry logic"""
    session = requests.Session()
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=RETRY_BACKOFF,
        status_forcelist=[408, 429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def make_api_request(session, method, endpoint, **kwargs):
    """Make an API request with error handling and retries"""
    url = f'http://localhost:11434/api/{endpoint}'
    logger.info(f"Making {method} request to {url} with parameters: {kwargs}")
    try:
        kwargs['timeout'] = kwargs.get('timeout', REQUEST_TIMEOUT)
        response = session.request(method, url, **kwargs)
        logger.info(f"Response Status: {response.status_code}")
        response.raise_for_status()
        return response
    except requests.exceptions.ConnectionError:
        logger.error("Connection to Ollama service lost. Please ensure Ollama is running.")
        return None
    except requests.exceptions.Timeout:
        logger.error("Request timed out. The operation took too long.")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        return None

def check_ollama_service(session):
    """Check if Ollama service is running and accessible"""
    response = make_api_request(session, 'GET', 'tags')
    return response is not None and response.status_code == 200

def create_modelfile():
    """Create the modelfile"""
    logger.info("Creating modelfile with specified parameters.")
    modelfile_content = f'''FROM llama3.2-3b

# Set parameters for optimal response generation
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
PARAMETER num_predict 1024
PARAMETER repeat_penalty 1.1
PARAMETER stop "Human:"
PARAMETER stop "Assistant:"

# Set the system message
SYSTEM """You are a highly knowledgeable water conservation expert AI focused on Turkey. Your primary role is to provide accurate, relevant, and direct answers to questions about water conservation, with special expertise in DSİ (State Hydraulic Works) and Turkish water management policies. Follow these guidelines:

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
   - Then, provide information directly related to that question
   - Include Turkey-specific context when relevant
   - If the question is not about water conservation, politely redirect to water-related topics

5. Handling Greetings:
   - For greetings like "hi" or "hello", respond with:
     "Hello! I'm your water conservation expert.\n\nHow can I help you save water today?"
   - Keep it professional and focused on water conservation"""'''
    
    modelfile_path = os.path.join(BASE_DIR, 'Modelfile')
    with open(modelfile_path, 'w', encoding='utf-8') as f:
        f.write(modelfile_content)
    logger.info("Modelfile created successfully.")
    return modelfile_path

def create_model(session, modelfile_path):
    """Create the model with retry logic"""
    logger.info(f"Creating model using modelfile at {modelfile_path}")
    
    # Check if model exists
    response = make_api_request(session, 'GET', 'tags')
    if response and response.status_code == 200:
        models = response.json().get('models', [])
        if any(model.get('name') == 'water-expert' for model in models):
            logger.info("Model 'water-expert' already exists, proceeding with training.")
            return True
    
    # Read Modelfile
    try:
        with open(modelfile_path, 'r', encoding='utf-8') as f:
            modelfile_content = f.read()
    except Exception as e:
        logger.error(f"Error reading Modelfile: {str(e)}")
        return False
    
    # Create model
    response = make_api_request(
        session,
        'POST',
        'create',
        json={'name': 'water-expert', 'modelfile': modelfile_content},
        timeout=300
    )
    
    if response and response.status_code == 200:
        logger.info("Model 'water-expert' created successfully")
        return True
    return False

def load_training_data(dataset_path):
    """Load and validate training data with progress bar"""
    logger.info(f"Loading training data from {dataset_path}")
    
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        if not isinstance(raw_data, list):
            logger.error("Training data must be a list of examples")
            return None
            
        total_examples = len(raw_data)
        valid_examples = []
        
        # Process each example with progress bar
        progress = tqdm(raw_data, desc="Validating training data", unit="examples")
        for example in progress:
            messages = example.get('messages', [])
            if not messages:
                progress.write(f"Skipping example: No messages found")
                continue
                
            # Extract messages
            system_msg = next((msg['content'] for msg in messages if msg['role'] == 'system'), '')
            user_msg = next((msg['content'] for msg in messages if msg['role'] == 'user'), '')
            assistant_msg = next((msg['content'] for msg in messages if msg['role'] == 'assistant'), '')
            
            if not user_msg or not assistant_msg:
                progress.write(f"Skipping example: Missing user or assistant message")
                continue
            
            valid_examples.append({
                'system': system_msg,
                'user': user_msg,
                'assistant': assistant_msg
            })
            
            # Update progress description
            progress.set_description(
                f"Validating data - Valid: {len(valid_examples)}/{total_examples} "
                f"({(len(valid_examples)/total_examples)*100:.1f}%)"
            )
        
        logger.info(f"Found {len(valid_examples)} valid examples out of {total_examples}")
        return valid_examples
        
    except FileNotFoundError:
        logger.error(f"Training data file not found: {dataset_path}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing training data: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading training data: {e}")
        return None

def parse_response(response):
    """Parse streaming response from Ollama API.
    
    Args:
        response (requests.Response): The HTTP response object.
    
    Returns:
        tuple: A tuple containing parsed data (dict or None) and error message (str or None).
    """
    try:
        # Split response into lines and process each JSON object
        lines = response.text.strip().split('\n')
        full_response = ""
        last_response = None
        
        for line in lines:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if 'error' in data:
                    return None, data['error']
                if 'response' in data:
                    full_response += data['response']
                    last_response = data
            except json.JSONDecodeError:
                continue
        
        if last_response is None:
            return None, "No valid response data found"
            
        # Create a combined response object
        result = {
            'model': last_response.get('model'),
            'created_at': last_response.get('created_at'),
            'response': full_response,
            'done': last_response.get('done', False),
            'context': last_response.get('context', []),
            'total_duration': last_response.get('total_duration', 0),
            'load_duration': last_response.get('load_duration', 0),
            'prompt_eval_count': last_response.get('prompt_eval_count', 0),
            'eval_count': last_response.get('eval_count', 0),
            'eval_duration': last_response.get('eval_duration', 0)
        }
        return result, None
        
    except Exception as e:
        logger.error(f"Error parsing response: {str(e)}")
        logger.error(f"Response content: {response.text[:200]}...")  # Log first 200 chars
        return None, str(e)

def train_model():
    """Train the model with improved error handling"""
    logger.info("Starting model training")
    session = create_session()
    
    # Check Ollama service
    if not check_ollama_service(session):
        logger.error("\nError: Could not connect to Ollama service.")
        logger.error("Please make sure Ollama is running by:")
        logger.error("1. Opening a new terminal/command prompt")
        logger.error("2. Running the command: ollama serve")
        logger.error("3. Waiting for Ollama to start")
        logger.error("4. Running this script again")
        return
    
    # Create modelfile
    modelfile_path = create_modelfile()
    
    # Create model
    if not create_model(session, modelfile_path):
        logger.error("Failed to create model. Please check the errors above.")
        return
    
    # Initialize TensorBoard
    log_dir = os.path.join(BASE_DIR, 'logs', 'tensorboard')
    os.makedirs(log_dir, exist_ok=True)
    writer = SummaryWriter(log_dir)
    
    # Load and validate training data
    dataset_path = os.path.join(BASE_DIR, 'dataset', 'wc-train.json')
    training_data = load_training_data(dataset_path)
    if not training_data:
        logger.error("No valid training data found. Exiting.")
        return
    
    # Training loop with progress bar
    total_examples = len(training_data)
    successful = 0
    failed = 0
    
    # Main training loop with progress bar
    progress_bar = tqdm(enumerate(training_data, 1), total=total_examples,
                       desc="Training model", unit="examples")
    
    for i, example in progress_bar:
        # Format the training prompt
        prompt = f"""System: {example['system']}
Human: {example['user']}
Assistant: {example['assistant']}"""
        
        # Make training request
        response = make_api_request(
            session,
            'POST',
            'generate',
            json={
                'model': 'water-expert',
                'prompt': prompt,
                'system': example['system'],
                'template': '{{.System}}\n\nHuman: {{.Prompt}}\nAssistant: {{.Response}}',
                'options': {
                    'temperature': 0.7,
                    'num_predict': 4096,
                    'top_p': 0.9,
                    'repeat_penalty': 1.1
                }
            }
        )
        
        if response and response.status_code == 200:
            response_data, error = parse_response(response)
            if response_data:
                successful += 1
                if 'loss' in response_data:
                    writer.add_scalar('Loss/train', response_data['loss'], i)
                    progress_bar.set_postfix({
                        'loss': f"{response_data['loss']:.4f}",
                        'success_rate': f"{(successful/i)*100:.1f}%"
                    })
            else:
                failed += 1
                if error:
                    progress_bar.write(f"Error in example {i}: {error}")
        else:
            failed += 1
            # Check if Ollama is still running
            if not check_ollama_service(session):
                progress_bar.write("\nLost connection to Ollama service. Please restart Ollama and the script.")
                break
        
        # Update progress description
        progress_bar.set_description(
            f"Training model - Success: {successful}/{i} ({(successful/i)*100:.1f}%)"
        )
        
        # Adaptive delay based on success rate
        delay = 0.05 if (successful/i) > 0.9 else 0.1
        time.sleep(delay)
    
    # Final stats
    logger.info("\nTraining completed!")
    logger.info(f"Total examples processed: {total_examples}")
    logger.info(f"Successful: {successful}, Failed: {failed}")
    writer.close()

# Main execution wrapped in try-except for keyboard interrupt
if __name__ == "__main__":
    try:
        train_model()
    except KeyboardInterrupt:
        logger.info("\nTraining interrupted by user.")
        logger.info("Cleaning up resources...")
