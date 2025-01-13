import requests
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def query_model(prompt, system_message=""):
    """Query the trained model with a prompt."""
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'water-expert',
                'prompt': prompt,
                'system': system_message,
                'options': {
                    'temperature': 0.7,
                    'num_predict': 4096,
                    'top_p': 0.9,
                    'repeat_penalty': 1.1
                }
            },
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"Error: API returned status code {response.status_code}")
            return None
            
        # Process streaming response
        full_response = ""
        for line in response.text.strip().split('\n'):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if 'error' in data:
                    logger.error(f"API Error: {data['error']}")
                    return None
                if 'response' in data:
                    full_response += data['response']
            except json.JSONDecodeError:
                continue
                
        return full_response.strip()
        
    except Exception as e:
        logger.error(f"Error querying model: {e}")
        return None

def evaluate_response(question, response, expected_keywords):
    """Evaluate the response based on expected keywords and criteria."""
    if not response:
        return False, "No response received"
    
    # Convert to lower case for case-insensitive matching
    response_lower = response.lower()
    
    # Check if response contains expected keywords
    found_keywords = [kw for kw in expected_keywords if kw.lower() in response_lower]
    keyword_score = len(found_keywords) / len(expected_keywords) if expected_keywords else 0
    
    # Check response length (should be between 50 and 1000 characters)
    length_ok = 50 <= len(response) <= 1000
    
    # Check if response is relevant to water conservation
    water_terms = ['su', 'water', 'dsi', 'conservation', 'drought', 'irrigation', 'resource']
    relevance_score = sum(1 for term in water_terms if term in response_lower) / len(water_terms)
    
    # Calculate overall score
    total_score = (keyword_score * 0.6) + (0.2 if length_ok else 0) + (relevance_score * 0.2)
    
    # Generate evaluation message
    if total_score >= 0.8:
        return True, f"Excellent (Score: {total_score:.2f})"
    elif total_score >= 0.6:
        return True, f"Good (Score: {total_score:.2f})"
    elif total_score >= 0.4:
        return True, f"Fair (Score: {total_score:.2f})"
    else:
        return False, f"Poor (Score: {total_score:.2f})"

def test_model():
    """Run a comprehensive test with 50 questions."""
    test_cases = [
        {
            "question": "What are DSİ's main responsibilities in Turkey?",
            "keywords": ["water management", "dams", "irrigation", "flood control", "hydroelectric"]
        },
        {
            "question": "How does DSİ monitor water quality in reservoirs?",
            "keywords": ["testing", "parameters", "monitoring", "quality control", "standards"]
        },
        {
            "question": "What measures are taken to prevent water pollution in Turkish lakes?",
            "keywords": ["regulations", "treatment", "monitoring", "protection", "waste management"]
        },
        {
            "question": "How does Turkey manage drought conditions?",
            "keywords": ["monitoring", "restrictions", "planning", "conservation", "emergency measures"]
        },
        {
            "question": "What role does DSİ play in agricultural irrigation?",
            "keywords": ["irrigation systems", "water allocation", "efficiency", "infrastructure"]
        },
        {
            "question": "How are groundwater resources managed in Turkey?",
            "keywords": ["monitoring", "permits", "extraction", "aquifers", "sustainability"]
        },
        {
            "question": "What technologies does DSİ use for water conservation?",
            "keywords": ["smart meters", "monitoring", "automation", "efficiency", "technology"]
        },
        {
            "question": "How does Turkey handle wastewater treatment?",
            "keywords": ["treatment plants", "recycling", "standards", "infrastructure"]
        },
        {
            "question": "What are Turkey's water conservation goals for 2025?",
            "keywords": ["targets", "efficiency", "reduction", "sustainability", "planning"]
        },
        {
            "question": "How does DSİ manage dam operations during floods?",
            "keywords": ["monitoring", "control", "safety", "emergency", "procedures"]
        },
        {
            "question": "What measures are taken to protect wetlands in Turkey?",
            "keywords": ["conservation", "regulations", "protection", "biodiversity"]
        },
        {
            "question": "How does DSİ coordinate with municipalities for water supply?",
            "keywords": ["coordination", "infrastructure", "distribution", "management"]
        },
        {
            "question": "What strategies are used for rainwater harvesting in Turkey?",
            "keywords": ["collection", "storage", "systems", "utilization"]
        },
        {
            "question": "How does Turkey manage cross-border water resources?",
            "keywords": ["agreements", "cooperation", "management", "international"]
        },
        {
            "question": "What role does DSİ play in hydroelectric power generation?",
            "keywords": ["dams", "power", "generation", "management", "infrastructure"]
        },
        {
            "question": "How are water tariffs determined in Turkey?",
            "keywords": ["pricing", "consumption", "rates", "policy"]
        },
        {
            "question": "What measures are taken during water shortages?",
            "keywords": ["restrictions", "conservation", "emergency", "management"]
        },
        {
            "question": "How does DSİ maintain water infrastructure?",
            "keywords": ["maintenance", "repairs", "monitoring", "upgrades"]
        },
        {
            "question": "What are Turkey's policies on water reuse?",
            "keywords": ["recycling", "treatment", "standards", "applications"]
        },
        {
            "question": "How does DSİ handle emergency water situations?",
            "keywords": ["response", "management", "procedures", "coordination"]
        },
        {
            "question": "What role does DSİ play in urban water management?",
            "keywords": ["infrastructure", "supply", "distribution", "planning"]
        },
        {
            "question": "How are water quality standards enforced in Turkey?",
            "keywords": ["monitoring", "testing", "enforcement", "regulations"]
        },
        {
            "question": "What measures protect drinking water sources?",
            "keywords": ["protection", "treatment", "monitoring", "safety"]
        },
        {
            "question": "How does DSİ manage seasonal water variations?",
            "keywords": ["planning", "storage", "management", "distribution"]
        },
        {
            "question": "What water conservation education programs exist in Turkey?",
            "keywords": ["education", "awareness", "programs", "public"]
        },
        {
            "question": "How does DSİ handle water rights allocation?",
            "keywords": ["rights", "allocation", "management", "permits"]
        },
        {
            "question": "What measures reduce agricultural water waste?",
            "keywords": ["efficiency", "irrigation", "technology", "management"]
        },
        {
            "question": "How are water resources mapped in Turkey?",
            "keywords": ["mapping", "monitoring", "assessment", "data"]
        },
        {
            "question": "What role does DSİ play in climate change adaptation?",
            "keywords": ["adaptation", "planning", "measures", "strategy"]
        },
        {
            "question": "How is industrial water use regulated?",
            "keywords": ["regulations", "permits", "monitoring", "standards"]
        },
        {
            "question": "What water conservation technologies are promoted?",
            "keywords": ["efficiency", "technology", "innovation", "solutions"]
        },
        {
            "question": "How does DSİ manage reservoir levels?",
            "keywords": ["monitoring", "control", "management", "operations"]
        },
        {
            "question": "What measures protect coastal water resources?",
            "keywords": ["protection", "management", "monitoring", "conservation"]
        },
        {
            "question": "How are water infrastructure projects funded?",
            "keywords": ["funding", "investment", "budget", "financing"]
        },
        {
            "question": "What role does DSİ play in research?",
            "keywords": ["research", "studies", "development", "innovation"]
        },
        {
            "question": "How is water quality monitored in rivers?",
            "keywords": ["monitoring", "testing", "parameters", "quality"]
        },
        {
            "question": "What drought prediction methods are used?",
            "keywords": ["prediction", "monitoring", "analysis", "forecasting"]
        },
        {
            "question": "How does DSİ coordinate emergency responses?",
            "keywords": ["coordination", "response", "emergency", "management"]
        },
        {
            "question": "What water conservation incentives exist?",
            "keywords": ["incentives", "programs", "benefits", "support"]
        },
        {
            "question": "How are water losses minimized in distribution?",
            "keywords": ["efficiency", "maintenance", "monitoring", "reduction"]
        },
        {
            "question": "What role does DSİ play in urban planning?",
            "keywords": ["planning", "development", "coordination", "infrastructure"]
        },
        {
            "question": "How is groundwater extraction regulated?",
            "keywords": ["regulation", "permits", "monitoring", "control"]
        },
        {
            "question": "What measures protect water infrastructure?",
            "keywords": ["security", "maintenance", "protection", "monitoring"]
        },
        {
            "question": "How does DSİ handle water disputes?",
            "keywords": ["resolution", "mediation", "management", "coordination"]
        },
        {
            "question": "What role does technology play in water management?",
            "keywords": ["technology", "innovation", "systems", "automation"]
        },
        {
            "question": "How are water conservation goals measured?",
            "keywords": ["metrics", "monitoring", "assessment", "evaluation"]
        },
        {
            "question": "What flood prevention measures are used?",
            "keywords": ["prevention", "control", "infrastructure", "management"]
        },
        {
            "question": "How does DSİ manage water during peak demand?",
            "keywords": ["management", "distribution", "planning", "control"]
        },
        {
            "question": "What role does public participation play?",
            "keywords": ["participation", "engagement", "consultation", "involvement"]
        },
        {
            "question": "How is water quality data managed?",
            "keywords": ["data", "management", "analysis", "reporting"]
        },
        {
            "question": "What measures ensure sustainable water use?",
            "keywords": ["sustainability", "conservation", "efficiency", "management"]
        }
    ]
    
    logger.info("Starting comprehensive model testing...")
    logger.info(f"Total test cases: {len(test_cases)}")
    
    results = {
        "total": len(test_cases),
        "passed": 0,
        "failed": 0,
        "scores": []
    }
    
    for i, test_case in enumerate(test_cases, 1):
        question = test_case["question"]
        keywords = test_case["keywords"]
        
        logger.info(f"\nTest {i}/{len(test_cases)}: {question}")
        response = query_model(question)
        
        if response:
            passed, evaluation = evaluate_response(question, response, keywords)
            if passed:
                results["passed"] += 1
            else:
                results["failed"] += 1
            
            logger.info("Response:")
            logger.info("-" * 40)
            logger.info(response)
            logger.info("-" * 40)
            logger.info(f"Evaluation: {evaluation}")
            results["scores"].append(float(evaluation.split()[-1].strip("()")))
        else:
            logger.error("Failed to get response")
            results["failed"] += 1
            results["scores"].append(0.0)
        
        # Add a small delay between requests
        if i < len(test_cases):
            import time
            time.sleep(2)
    
    # Print summary
    logger.info("\n" + "="*50)
    logger.info("Testing Summary")
    logger.info("="*50)
    logger.info(f"Total Tests: {results['total']}")
    logger.info(f"Passed: {results['passed']} ({(results['passed']/results['total'])*100:.1f}%)")
    logger.info(f"Failed: {results['failed']} ({(results['failed']/results['total'])*100:.1f}%)")
    if results["scores"]:
        avg_score = sum(results["scores"]) / len(results["scores"])
        logger.info(f"Average Score: {avg_score:.2f}")
    logger.info("="*50)

if __name__ == "__main__":
    test_model()
