import os
import json
import requests
import logging
from typing import Dict, Any, Optional

class WaterBillOllamaChat:
    def __init__(self, 
                 ollama_host: str = 'http://localhost:11434', 
                 model: str = 'llama3.2'):
        """
        Initialize Ollama chat for water bill analysis in English
        
        Args:
            ollama_host (str): Ollama API host
            model (str): Ollama model to use
        """
        self.ollama_host = ollama_host
        self.model = model
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def generate_bill_analysis_prompt(self, bill_text: str, additional_instruction: str = '') -> str:
        """
        Generate a structured prompt for bill analysis in English
        
        Args:
            bill_text (str): Extracted text from water bill
            additional_instruction (str): Extra processing instructions
        
        Returns:
            Structured prompt for bill analysis
        """
        base_prompt = f"""Analyze the following water bill text and provide a comprehensive, structured report in ENGLISH:

STRICT INSTRUCTIONS:
- Use ONLY ENGLISH language
- Provide clear, professional analysis
- Format the analysis using clean, readable text
- Use Turkish Lira (TRY) for all monetary values
- Include detailed sections: Bill Details, Customer Information, Water Consumption, Charges and Taxes
- Provide actionable water-saving recommendations

Bill Text:
{bill_text}

{additional_instruction}

EXPECTED OUTPUT FORMAT:
```
Bill Details
------------
- Bill Number: [Extract from bill]
- Date: [Extract from bill]
- Account Number: [Extract from bill]

Customer Information
-------------------
- Name: [Extract from bill]
- Address: [Full address details]

Water Consumption
-----------------
- Total Consumption: X m³
- Billing Period: [Date range]

Financial Summary
-----------------
- Water Charge: X.XX TRY
- Sewage Charge: Y.YY TRY
- Total Bill: Z.ZZ TRY

Water Conservation Tips
----------------------
1. Practical tip with potential water/cost savings
2. Another actionable recommendation
3. Easy-to-implement water-saving strategy

By implementing these recommendations, you can reduce water consumption and lower your utility expenses.
```

Provide a detailed, precise analysis following this structure. WRITE EVERYTHING IN ENGLISH."""

        return base_prompt

    def chat_with_ollama(self, 
                          bill_text: str, 
                          additional_instruction: str = '', 
                          context: Optional[list] = None) -> Dict[str, Any]:
        """
        Send bill text to Ollama for analysis in English
        
        Args:
            bill_text (str): Extracted text from water bill
            additional_instruction (str): Extra processing instructions
            context (list, optional): Conversation context
        
        Returns:
            Dict containing analysis response
        """
        try:
            prompt = self.generate_bill_analysis_prompt(bill_text, additional_instruction)
            
            payload = {
                'model': self.model,
                'prompt': prompt,
                'stream': False,
                'context': context or []
            }
            
            response = requests.post(
                f'{self.ollama_host}/api/generate', 
                json=payload, 
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                'success': True,
                'response': result.get('response', 'No analysis available'),
                'context': result.get('context', [])
            }
        
        except requests.RequestException as e:
            self.logger.error(f"Ollama API error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def analyze_water_bill(self, 
                            bill_text: str, 
                            additional_instruction: str = '') -> Dict[str, Any]:
        """
        Comprehensive water bill analysis method in English
        
        Args:
            bill_text (str): Extracted text from water bill
            additional_instruction (str): Extra processing instructions
        
        Returns:
            Comprehensive bill analysis
        """
        return self.chat_with_ollama(bill_text, additional_instruction)

def create_water_bill_chat(language: str = 'en') -> WaterBillOllamaChat:
    """
    Factory function to create WaterBillOllamaChat instance
    
    Args:
        language (str): Preferred output language (always English)
    
    Returns:
        WaterBillOllamaChat instance
    """
    return WaterBillOllamaChat()

# Example usage
if __name__ == '__main__':
    # Sample bill text for testing
    sample_bill = """"""
    
    bill_chat = create_water_bill_chat()
    instruction = "Provide comprehensive bill analysis in English with Turkish Lira pricing"
    analysis = bill_chat.analyze_water_bill(sample_bill, instruction)
    print(json.dumps(analysis, indent=2, ensure_ascii=False))

# Main block to demonstrate direct Ollama interaction
if __name__ == '__main__':
    # Sample bill text for testing
    sample_bill = """"""
    
    bill_chat = create_water_bill_chat()
    instruction = "Give bill information tidy, use only english text, use turkish liras unit for pricement, give advice for bill varibles water saving tips"
    
    # Directly print the response
    analysis = bill_chat.analyze_water_bill(sample_bill, instruction)
    print(analysis['response'])