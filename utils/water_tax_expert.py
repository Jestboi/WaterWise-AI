import os
import logging
import json
from typing import Dict, Tuple, Optional, Any

class WaterTaxExpert:
    def __init__(self, context: str = 'bill_analysis'):
        """
        Initialize Water Tax Expert with specific context
        
        Args:
            context (str): Context for the expert's analysis
        """
        self.logger = logging.getLogger(__name__)
        self.context = context
    
    def format_bill_analysis(self, bill_analysis: Dict[str, Any]) -> str:
        """
        Format bill analysis into a structured, readable prompt
        
        Args:
            bill_analysis (Dict): Comprehensive bill analysis dictionary
        
        Returns:
            Formatted string for model input
        """
        try:
            # Create a structured, readable format for bill analysis
            formatted_analysis = "Water Bill Analysis Details:\n\n"
            
            # Add key bill details with clear labeling
            key_details = [
                ('Total Consumption', 'm³'),
                ('Water Cost', 'TL'),
                ('Wastewater Cost', 'TL'),
                ('Total Bill', 'TL'),
                ('Billing Period', ''),
                ('Reading Days', 'days')
            ]
            
            for label, unit in key_details:
                value = bill_analysis.get(label.lower().replace(' ', '_'), 'N/A')
                formatted_analysis += f"{label}: {value} {unit}\n"
            
            # Add any additional insights or metrics
            formatted_analysis += "\nAdditional Insights:\n"
            for key, value in bill_analysis.items():
                if key.lower() not in [detail[0].lower().replace(' ', '_') for detail in key_details]:
                    formatted_analysis += f"{key.replace('_', ' ').title()}: {value}\n"
            
            return formatted_analysis
        
        except Exception as e:
            self.logger.error(f"Error formatting bill analysis: {e}")
            return str(bill_analysis)
    
    def generate_bill_explanation(self, bill_analysis: Dict[str, Any]) -> Tuple[str, Optional[str]]:
        """
        Generate a comprehensive explanation of the bill analysis
        
        Args:
            bill_analysis (Dict): Comprehensive bill analysis dictionary
        
        Returns:
            Tuple of (explanation, error)
        """
        try:
            # Format the bill analysis
            formatted_analysis = self.format_bill_analysis(bill_analysis)
            
            # Predefined expert response template
            explanation = f"""Water Bill Analysis and Recommendations:

Detailed Bill Breakdown:
{formatted_analysis}

Key Insights:
1. Consumption Analysis:
   - Your water consumption provides insights into your usage patterns
   - Understanding these patterns helps in conservation efforts

2. Cost Efficiency:
   - Analyze your water costs and identify potential savings
   - Look for opportunities to reduce water usage

3. Conservation Recommendations:
   - Consider installing water-efficient fixtures
   - Check for leaks and repair them promptly
   - Use water-saving techniques in daily activities

4. Environmental Impact:
   - Reducing water consumption helps conserve local water resources
   - Lower water usage contributes to sustainable living

5. Financial Savings:
   - Implementing water-saving strategies can lead to significant bill reductions
   - Small changes can result in meaningful cost savings

Personalized Advice:
Based on your bill analysis, focus on understanding your consumption patterns 
and identifying areas where you can reduce water usage."""
            
            return explanation, None
        
        except Exception as e:
            error_msg = f"Error generating bill explanation: {str(e)}"
            self.logger.error(error_msg)
            return "", error_msg

    def generate_response(self, message: str) -> Tuple[str, Optional[str]]:
        """
        Generate a comprehensive water bill analysis response
        
        Args:
            message (str): User's input message (bill details)
        
        Returns:
            Tuple of (response, error)
        """
        try:
            # Analyze the bill details
            bill_details = self._extract_bill_details(message)
            
            # Calculate daily average consumption
            try:
                total_consumption = float(bill_details.get('total_consumption', '0').replace('m³', '').strip())
                reading_days = float(bill_details.get('reading_days', '1'))
                daily_avg = total_consumption / reading_days if reading_days > 0 else 0
                daily_avg = round(daily_avg, 2)
            except (ValueError, TypeError, ZeroDivisionError):
                total_consumption = 0
                reading_days = 1
                daily_avg = 0
            
            # Generate comprehensive response
            response = f"""Ankara Büyükşehir Belediyesi ASKI - Su Faturası Analizi

Fatura Genel Bilgileri
Fatura No: {bill_details.get('bill_number', 'Bulunamadı')}
Abone No: {bill_details.get('subscriber_no', 'Bulunamadı')}
Sözleşme No: {bill_details.get('contract_no', 'Bulunamadı')}
Abone Adı: {bill_details.get('subscriber_name', 'Bulunamadı')}
Adres: {bill_details.get('address', 'Bulunamadı')}
Fatura Tarihi: {bill_details.get('bill_date', 'Bulunamadı')}
Tebligat Saati: {bill_details.get('notification_time', 'Bulunamadı')}
Son Ödeme Tarihi: {bill_details.get('payment_deadline', 'Bulunamadı')}

Su Tüketim Detayları
Son Endeks: {bill_details.get('last_index', 'Bulunamadı')}
İlk Endeks: {bill_details.get('first_index', 'Bulunamadı')}
Tüketim: {total_consumption} m³
Okuma Gün Sayısı: {reading_days} gün
Günlük Ortalama Tüketim: {daily_avg} m³

Fatura Detayları
Kalem	Tutar (TL)
Su Bedeli (1. Kademe)	{bill_details.get('water_cost', '0.00')}
Atıksu Bedeli	{bill_details.get('wastewater_cost', '0.00')}
ÇTV (Çevre Temizlik Vergisi)	{bill_details.get('environment_tax', '0.00')}
Su KDV (%1)	{bill_details.get('water_vat_1', '0.00')}
Atıksu KDV (%10)	{bill_details.get('wastewater_vat_10', '0.00')}
Diğer Bedeller	{bill_details.get('other_charges', '0.00')}
Toplam Tutar	{bill_details.get('total_bill', '0.00')}"""
            
            return response, None
        
        except Exception as e:
            error_msg = f"Yanıt oluşturma hatası: {str(e)}"
            self.logger.error(error_msg)
            return "", error_msg

    def _extract_bill_details(self, bill_text: str) -> Dict[str, str]:
        """
        Extract structured details from the bill text
        
        Args:
            bill_text (str): Full bill text
        
        Returns:
            Dictionary of extracted bill details
        """
        try:
            details = {
                'bill_number': self._extract_value(bill_text, r'Fatura No:\s*(\d+)', 'Bulunamadı'),
                'subscriber_no': self._extract_value(bill_text, r'Abone No:\s*(\d+)', 'Bulunamadı'),
                'contract_no': self._extract_value(bill_text, r'Sözleşme No:\s*(\d+)', 'Bulunamadı'),
                'subscriber_name': self._extract_value(bill_text, r'Abone Adı:\s*([^\n]+)', 'Bulunamadı'),
                'address': self._extract_value(bill_text, r'Adres:\s*([^\n]+)', 'Bulunamadı'),
                'bill_date': self._extract_value(bill_text, r'Fatura Tarihi:\s*(\d{2}\.\d{2}\.\d{4})', 'Bulunamadı'),
                'notification_time': self._extract_value(bill_text, r'Tebligat Saati:\s*(\d{2}:\d{2}:\d{2})', 'Bulunamadı'),
                'payment_deadline': self._extract_value(bill_text, r'Son Ödeme Tarihi:\s*(\d{2}\.\d{2}\.\d{4})', 'Bulunamadı'),
                
                'last_index': self._extract_value(bill_text, r'Son Endeks:\s*(\d+)', '0'),
                'first_index': self._extract_value(bill_text, r'İlk Endeks:\s*(\d+)', '0'),
                'total_consumption': self._extract_value(bill_text, r'Tüketim:\s*(\d+)\s*m³', '0'),
                'reading_days': self._extract_value(bill_text, r'Okuma Gün Sayısı:\s*(\d+)', '0'),
                
                'water_cost': self._extract_value(bill_text, r'Su Bedeli \(1\. Kademe\):\s*(\d+(?:\.\d+)?)', '0.00'),
                'wastewater_cost': self._extract_value(bill_text, r'Atıksu Bedeli:\s*(\d+(?:\.\d+)?)', '0.00'),
                'environment_tax': self._extract_value(bill_text, r'ÇTV \(Çevre Temizlik Vergisi\):\s*(\d+(?:\.\d+)?)', '0.00'),
                'water_vat_1': self._extract_value(bill_text, r'Su KDV \(%1\):\s*(\d+(?:\.\d+)?)', '0.00'),
                'wastewater_vat_10': self._extract_value(bill_text, r'Atıksu KDV \(%10\):\s*(\d+(?:\.\d+)?)', '0.00'),
                'other_charges': '0.00',
                'total_bill': self._extract_value(bill_text, r'Toplam Tutar:\s*(\d+(?:\.\d+)?)', '0.00')
            }
            
            # Additional validation
            if details['total_consumption'] == '0':
                try:
                    last_index = float(details['last_index'])
                    first_index = float(details['first_index'])
                    details['total_consumption'] = str(max(0, last_index - first_index))
                except (ValueError, TypeError):
                    details['total_consumption'] = '0'
            
            return details
        
        except Exception as e:
            self.logger.error(f"Bill details extraction error: {str(e)}")
            return {
                'bill_number': 'Bulunamadı',
                'total_consumption': '0',
                'reading_days': '0',
                'total_bill': '0.00'
            }

    def _extract_value(self, text: str, pattern: str, default: str = 'N/A') -> str:
        """
        Extract a value from text using a regex pattern
        
        Args:
            text (str): Full text to search
            pattern (str): Regex pattern to match
            default (str): Default value if no match found
        
        Returns:
            Extracted value or default
        """
        import re
        
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        return match.group(1).strip() if match else default

def create_water_expert(context: str = 'bill_analysis') -> WaterTaxExpert:
    """
    Factory function to create a Water Tax Expert instance
    
    Args:
        context (str): Context for the expert's analysis
    
    Returns:
        WaterTaxExpert instance
    """
    return WaterTaxExpert(context)
