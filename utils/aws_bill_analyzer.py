import boto3
import os
import re
import json
from typing import Dict, List, Union
from werkzeug.utils import secure_filename

class AWSBillAnalyzer:
    def __init__(self, upload_folder, region_name='us-east-1'):
        """
        Initialize AWS Textract Analyzer
        
        Args:
            upload_folder (str): Path to store uploaded files
            region_name (str): AWS region to use
        """
        self.upload_folder = upload_folder
        os.makedirs(upload_folder, exist_ok=True)
        
        # Initialize Textract client
        self.textract_client = boto3.client('textract', region_name=region_name)

    def _detect_document_text(self, document_path: str) -> Dict:
        """
        Detect text in a document using AWS Textract
        
        Args:
            document_path (str): Path to the document file
        
        Returns:
            Dict: Detected text and metadata
        """
        # Read document bytes
        with open(document_path, 'rb') as document:
            document_bytes = document.read()
        
        # Call Textract API
        response = self.textract_client.detect_document_text(
            Document={'Bytes': document_bytes}
        )
        
        # Extract text blocks with their geometry
        text_blocks = [
            {
                'text': block['Text'],
                'block_type': block['BlockType'],
                'confidence': block.get('Confidence', 0),
                'geometry': block.get('Geometry', {})
            } 
            for block in response['Blocks'] 
            if block['BlockType'] in ['LINE', 'WORD']
        ]
        
        # Reconstruct full text
        full_text = ' '.join(block['text'] for block in text_blocks if block['block_type'] == 'LINE')
        
        return {
            'full_text': full_text,
            'text_blocks': text_blocks
        }

    def _parse_bill_details(self, full_text: str) -> Dict[str, str]:
        """
        Parse bill details from extracted text using advanced regex and pattern matching
        
        Args:
            full_text (str): Full extracted text
        
        Returns:
            Dict of parsed bill details
        """
        # Predefined regex patterns for bill details
        patterns = {
            'total_amount': [
                r'(?:Total|Toplam)\s*(?:Amount|Tutar)[:]*\s*[₺$]*\s*(\d+(?:\.\d{1,2})?)',
                r'(?:Fatura|Invoice)\s*(?:Tutarı|Amount)[:]*\s*[₺$]*\s*(\d+(?:\.\d{1,2})?)'
            ],
            'billing_period': [
                r'(?:Billing|Fatura)\s*(?:Period|Dönemi)[:]*\s*(\w+\s*\d{4}\s*-\s*\w+\s*\d{4})',
                r'(?:Dönem|Period)[:]*\s*(\d{2}/\d{4}\s*-\s*\d{2}/\d{4})'
            ],
            'water_consumption': [
                r'(?:Water|Su)\s*(?:Consumption|Tüketimi)[:]*\s*(\d+(?:\.\d{1,2})?)\s*(?:m3|cubic\s*meters)',
                r'(?:Tüketim|Consumption)[:]*\s*(\d+(?:\.\d{1,2})?)\s*m3'
            ],
            'tax_rate': [
                r'(?:Tax|Vergi)\s*(?:Rate|Oranı)[:]*\s*(\d+(?:\.\d{1,2})?)%',
                r'(?:KDV|VAT)\s*(?:Oranı|Rate)[:]*\s*(%\d+(?:\.\d{1,2})?)'
            ],
            'customer_name': [
                r'(?:Müşteri|Customer)\s*(?:Adı|Name)[:]*\s*([A-ZÇŞĞÜİÖa-zçşğüıö\s]+)',
                r'(?:Ad\s*Soyad|Full\s*Name)[:]*\s*([A-ZÇŞĞÜİÖa-zçşğüıö\s]+)'
            ],
            'address': [
                r'(?:Adres|Address)[:]*\s*([A-ZÇŞĞÜİÖa-zçşğüıö\s\d,.-]+)',
                r'(?:Lokasyon|Location)[:]*\s*([A-ZÇŞĞÜİÖa-zçşğüıö\s\d,.-]+)'
            ]
        }
        
        # Extract details
        bill_details = {}
        for key, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, full_text, re.IGNORECASE | re.UNICODE)
                if match:
                    bill_details[key] = match.group(1)
                    break
        
        return bill_details

    def process_bill(self, file_path: str) -> Dict[str, Union[str, bool]]:
        """
        Process a bill file using AWS Textract
        
        Args:
            file_path (str): Path to the bill file
        
        Returns:
            Dict containing parsed bill details
        """
        try:
            # Detect document text
            text_detection = self._detect_document_text(file_path)
            
            # Parse bill details
            bill_details = self._parse_bill_details(text_detection['full_text'])
            
            # Combine results
            result = {
                'success': True,
                'full_text': text_detection['full_text'],
                'text_blocks': text_detection['text_blocks'],
                **bill_details,
                'raw_output': json.dumps({
                    'full_text': text_detection['full_text'],
                    'text_blocks': text_detection['text_blocks'],
                    'parsed_details': bill_details
                }, indent=2)
            }
            
            return result
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'raw_output': str(e)
            }

def allowed_file(filename: str) -> bool:
    """
    Check if the file type is allowed for AWS Textract
    
    Args:
        filename (str): Name of the file
    
    Returns:
        bool: True if file is allowed, False otherwise
    """
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
