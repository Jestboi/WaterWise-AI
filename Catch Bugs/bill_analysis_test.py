import os
import sys
import logging
import json
import boto3
from typing import Dict, Any
import re
import io

# Reconfigure stdout to use UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.advanced_bill_analyzer import analyze_water_bill

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_bill_with_advanced_analysis(bill_text: str) -> Dict[str, Any]:
    """
    Process bill text with advanced analysis and structured output
    
    Args:
        bill_text (str): Raw bill text
    
    Returns:
        Comprehensive bill analysis dictionary
    """
    # Normalize Turkish characters
    def normalize_turkish(text):
        replacements = {
            'İ': 'I', 'ı': 'i', 'Ş': 'S', 'ş': 's', 
            'Ğ': 'G', 'ğ': 'g', 'Ü': 'U', 'ü': 'u', 
            'Ö': 'O', 'ö': 'o', 'Ç': 'C', 'ç': 'c'
        }
        for turkish, normalized in replacements.items():
            text = text.replace(turkish, normalized)
        return text

    bill_text = normalize_turkish(bill_text)

    # Parsing patterns for water bill
    bill_details = {
        'bill_number': re.findall(r'FATURA NO[:]*\s*(\d+)', bill_text),
        'subscriber_number': re.findall(r'ABONE NO\s*(\d+)', bill_text),
        'billing_period': re.findall(r'DONEM\s*(\d{4}-\d{2})', bill_text),
        'total_consumption': re.findall(r'TUKETIM \(m3\)[:]*\s*(\d+(?:\.\d+)?)', bill_text),
        'water_cost': re.findall(r'SU BEDELI \(TL\)[:]*\s*(\d+(?:\.\d+)?)', bill_text),
        'wastewater_cost': re.findall(r'ATIKSU BEDELI \(TL\)[:]*\s*(\d+(?:\.\d+)?)', bill_text),
        'total_bill': re.findall(r'TOPLAM BORC \(TL\)[:]*\s*(\d+(?:\.\d+)?)', bill_text),
        'reading_days': re.findall(r'OKUMA GUN SAYISI[:]*\s*(\d+)', bill_text)
    }

    # Extract first match or use default
    def safe_extract(data_list, default='N/A'):
        return data_list[0] if data_list else default

    # Compute derived metrics
    total_consumption = float(safe_extract(bill_details['total_consumption'], '0'))
    water_cost = float(safe_extract(bill_details['water_cost'], '0'))
    wastewater_cost = float(safe_extract(bill_details['wastewater_cost'], '0'))
    total_bill = float(safe_extract(bill_details['total_bill'], '0'))
    reading_days = int(safe_extract(bill_details['reading_days'], '1'))

    # Prevent division by zero
    cost_per_cubic_meter = water_cost / total_consumption if total_consumption > 0 else 0
    daily_average = total_consumption / reading_days if reading_days > 0 else 0

    # Structured analysis output
    analysisOutput = f"""Bill Analysis 1 Successfully Processed
Bill Details
- Bill Number: {safe_extract(bill_details['bill_number'])}
- Billing Period: {safe_extract(bill_details['billing_period'])}
- Subscriber Number: {safe_extract(bill_details['subscriber_number'])}

Financial Analysis
Cost per cubic meter: {cost_per_cubic_meter:.2f} ₺/m³
Total bill: {total_bill:.2f} ₺
- Water Consumption Cost: {water_cost:.2f} ₺
- Wastewater Fee: {wastewater_cost:.2f} ₺

Consumption Analysis
Daily average: {daily_average:.2f} m³/day
Total consumption: {total_consumption:.2f} m³

Additional Insights:
- Reading Period: {reading_days} days
"""

    return {
        'raw_text': bill_text,
        'analysisOutput': analysisOutput,
        'details': {
            'bill_number': safe_extract(bill_details['bill_number']),
            'billing_period': safe_extract(bill_details['billing_period']),
            'total_consumption': total_consumption,
            'total_bill': total_bill,
            'water_cost': water_cost,
            'wastewater_cost': wastewater_cost,
            'cost_per_cubic_meter': cost_per_cubic_meter,
            'daily_average': daily_average
        }
    }

def analyze_bill_image(image_path):
    """
    Analyze bill image using AWS Textract and advanced bill analysis
    
    Args:
        image_path (str): Path to the bill image
    
    Returns:
        Comprehensive bill analysis
    """
    try:
        # Initialize Textract client
        textract_client = boto3.client('textract')
        
        # Read the image file
        with open(image_path, 'rb') as document:
            image_bytes = document.read()
        
        # Detect document text using Textract
        response = textract_client.detect_document_text(Document={'Bytes': image_bytes})
        
        # Extract text from the response
        extracted_text = ' '.join([item['Text'] for item in response.get('Blocks', []) 
                                   if item['BlockType'] == 'LINE'])
        
        # Log extracted text
        logger.info(f"Extracted Text Length: {len(extracted_text)} characters")
        
        # Process bill analysis
        bill_analysis = process_bill_with_advanced_analysis(extracted_text)
        
        return bill_analysis
    
    except Exception as e:
        logger.error(f"Bill image analysis failed: {e}")
        return None

def main():
    # Path to the bill image
    image_paths = [
        'uploads/20241229_165100.jpg',  # First bill
        'uploads/20241229_164839.jpg'   # Second bill
    ]
    
    # Analyze multiple bills
    for image_path in image_paths:
        print(f"\n--- Analyzing Bill: {image_path} ---")
        
        # Analyze the bill
        result = analyze_water_bill(image_path)
        
        if result:
            # Print Raw Text Details
            print("Raw Text Details:")
            print(result.get('raw_text', 'No raw text found'))
            
            # Print Bill Details
            print("\nBill Details:")
            details = result.get('details', {})
            
            # Pretty print the details
            print(json.dumps(details, indent=2, ensure_ascii=False))
        else:
            print("Bill analysis failed.")

if __name__ == '__main__':
    main()
