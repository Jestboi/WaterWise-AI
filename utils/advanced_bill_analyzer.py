import re
import logging
from typing import Dict, Any, List, Optional
import boto3
import json

class AdvancedBillAnalyzer:
    def __init__(self, language='tr'):
        """
        Initialize Advanced Bill Analyzer
        
        Args:
            language (str): Language for analysis (default: Turkish)
        """
        self.language = language
        self.logger = logging.getLogger(__name__)
        self.textract_client = boto3.client('textract')
    
    def normalize_turkish(self, text: str) -> str:
        """
        Normalize Turkish characters for consistent parsing
        
        Args:
            text (str): Input text
        
        Returns:
            str: Normalized text
        """
        replacements = {
            'İ': 'I', 'ı': 'i', 'Ş': 'S', 'ş': 's', 
            'Ğ': 'G', 'ğ': 'g', 'Ü': 'U', 'ü': 'u', 
            'Ö': 'O', 'ö': 'o', 'Ç': 'C', 'ç': 'c'
        }
        for turkish, normalized in replacements.items():
            text = text.replace(turkish, normalized)
        return text
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from bill image using AWS Textract
        
        Args:
            image_path (str): Path to bill image
        
        Returns:
            str: Extracted text from image
        """
        try:
            with open(image_path, 'rb') as document:
                image_bytes = document.read()
            
            response = self.textract_client.detect_document_text(Document={'Bytes': image_bytes})
            
            extracted_text = ' '.join([
                item['Text'] for item in response.get('Blocks', []) 
                if item['BlockType'] == 'LINE'
            ])
            
            return self.normalize_turkish(extracted_text)
        
        except Exception as e:
            self.logger.error(f"Text extraction failed: {e}")
            return ""
    
    def parse_water_bill(self, bill_text: str) -> Dict[str, Any]:
        """
        Parse water bill details from extracted text
        
        Args:
            bill_text (str): Extracted bill text
        
        Returns:
            Dict with parsed bill details
        """
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

        # Safe extraction helper
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
        return {
            'raw_text': bill_text,
            'details': {
                'bill_number': safe_extract(bill_details['bill_number']),
                'subscriber_number': safe_extract(bill_details['subscriber_number']),
                'billing_period': safe_extract(bill_details['billing_period']),
                'total_consumption': total_consumption,
                'water_cost': water_cost,
                'wastewater_cost': wastewater_cost,
                'total_bill': total_bill,
                'reading_days': reading_days,
                'cost_per_cubic_meter': cost_per_cubic_meter,
                'daily_average': daily_average
            }
        }
    
    def analyze_water_bill(self, image_path: str) -> Dict[str, Any]:
        """
        Comprehensive water bill analysis
        
        Args:
            image_path (str): Path to water bill image
        
        Returns:
            Comprehensive bill analysis
        """
        try:
            # Extract text from image
            extracted_text = self.extract_text_from_image(image_path)
            
            # Parse bill details
            bill_analysis = self.parse_water_bill(extracted_text)
            
            return bill_analysis
        
        except Exception as e:
            self.logger.error(f"Water bill analysis failed: {e}")
            return {}

    def process_bill_with_advanced_analysis(self, text: str) -> Dict[str, Any]:
        """
        Backwards compatibility function for processing bill text
        
        Args:
            text (str): Input bill text
        
        Returns:
            Comprehensive bill analysis dictionary
        """
        # Create analyzer instance
        analyzer = AdvancedBillAnalyzer()
        
        # Normalize text
        normalized_text = analyzer.normalize_turkish(text)
        
        # Parsing patterns for water bill
        bill_details = {
            'bill_number': re.findall(r'FATURA NO[:]*\s*(\d+)', normalized_text),
            'subscriber_number': re.findall(r'ABONE NO\s*(\d+)', normalized_text),
            'billing_period': re.findall(r'DONEM\s*(\d{4}-\d{2})', normalized_text),
            'total_consumption': re.findall(r'TUKETIM \(m3\)[:]*\s*(\d+(?:\.\d+)?)', normalized_text),
            'water_cost': re.findall(r'SU BEDELI \(TL\)[:]*\s*(\d+(?:\.\d+)?)', normalized_text),
            'wastewater_cost': re.findall(r'ATIKSU BEDELI \(TL\)[:]*\s*(\d+(?:\.\d+)?)', normalized_text),
            'total_bill': re.findall(r'TOPLAM BORC \(TL\)[:]*\s*(\d+(?:\.\d+)?)', normalized_text),
            'reading_days': re.findall(r'OKUMA GUN SAYISI[:]*\s*(\d+)', normalized_text)
        }

        # Safe extraction helper
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
- Fatura Numarası: {safe_extract(bill_details['bill_number'])}
- Abone Numarası: {safe_extract(bill_details['subscriber_number'])}
- Fatura Dönemi: {safe_extract(bill_details['billing_period'])}

Tüketim Analizi
- Toplam Tüketim: {total_consumption:.2f} m³
- Günlük Ortalama Tüketim: {daily_average:.2f} m³/gün
- Okuma Günü Sayısı: {reading_days} gün

Finansal Analiz
- Su Bedeli: {water_cost:.2f} ₺
- Atıksu Bedeli: {wastewater_cost:.2f} ₺
- Toplam Borç: {total_bill:.2f} ₺
- Metreküp Başına Maliyet: {cost_per_cubic_meter:.2f} ₺/m³

Ek Açıklamalar:
"""

        # Add consumption insights
        if total_consumption > 10:
            analysisOutput += "- Yüksek su tüketimi tespit edildi. Su tasarrufu teknikleri düşünülmelidir.\n"
        elif total_consumption < 5:
            analysisOutput += "- Düşük su tüketimi. Su tasarrufu konusunda harika bir iş!\n"

        return {
            'raw_text': normalized_text,
            'analysisOutput': analysisOutput,
            'bill_type': 'water_bill',
            'details': {
                'bill_number': safe_extract(bill_details['bill_number']),
                'subscriber_number': safe_extract(bill_details['subscriber_number']),
                'billing_period': safe_extract(bill_details['billing_period']),
                'total_consumption': total_consumption,
                'water_cost': water_cost,
                'wastewater_cost': wastewater_cost,
                'total_bill': total_bill,
                'reading_days': reading_days,
                'cost_per_cubic_meter': cost_per_cubic_meter,
                'daily_average': daily_average
            }
        }

def analyze_water_bill(image_path: str) -> Dict[str, Any]:
    """
    Convenience function to analyze water bill
    
    Args:
        image_path (str): Path to water bill image
    
    Returns:
        Comprehensive bill analysis
    """
    analyzer = AdvancedBillAnalyzer()
    return analyzer.analyze_water_bill(image_path)

def process_bill_with_advanced_analysis(text: str) -> Dict[str, Any]:
    """
    Backwards compatibility function to process bill text
    
    Args:
        text (str): Input bill text
    
    Returns:
        Comprehensive bill analysis dictionary
    """
    analyzer = AdvancedBillAnalyzer()
    return analyzer.process_bill_with_advanced_analysis(text)
