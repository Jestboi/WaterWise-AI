import os
import re
import json
import logging
import boto3
import numpy as np
import pandas as pd
from typing import Dict, List, Union, Any
from PIL import Image
import pytesseract
import cv2
import PyPDF2
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bill_analysis.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('IntelligentBillAnalyzer')

class IntelligentBillAnalyzer:
    def __init__(self, upload_folder='uploads'):
        """
        Initialize Intelligent Bill Analyzer with multi-format support
        
        Args:
            upload_folder (str): Directory to store temporary uploaded files
        """
        self.upload_folder = upload_folder
        os.makedirs(upload_folder, exist_ok=True)
        
        # Initialize AWS Textract client
        try:
            self.textract_client = boto3.client('textract')
            logger.info("AWS Textract client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Textract client: {e}")
            self.textract_client = None
        
        # Predefined bill parsing patterns (extensible)
        self.bill_patterns = {
            'water_bill': {
                'total_amount': [
                    r'(?:Toplam|Total)\s*(?:Tutar|Amount)[:]*\s*[₺$]*\s*(\d+(?:\.\d{1,2})?)',
                    r'(?:Fatura|Invoice)\s*(?:Tutarı|Amount)[:]*\s*[₺$]*\s*(\d+(?:\.\d{1,2})?)'
                ],
                'billing_period': [
                    r'(?:Dönem|Period)[:]*\s*(\d{2}/\d{4}\s*-\s*\d{02}/\d{4})',
                    r'(?:Fatura|Billing)\s*(?:Dönemi|Period)[:]*\s*(\w+\s*\d{4}\s*-\s*\w+\s*\d{4})'
                ],
                'water_consumption': [
                    r'(?:Su\s*Tüketimi|Water\s*Consumption)[:]*\s*(\d+(?:\.\d{1,2})?)\s*m3',
                    r'(?:Tüketim|Consumption)[:]*\s*(\d+(?:\.\d{1,2})?)\s*(?:m3|cubic\s*meters)'
                ]
            }
        }

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for better text extraction
        
        Args:
            image_path (str): Path to input image
        
        Returns:
            Preprocessed image as numpy array
        """
        logger.info(f"Preprocessing image: {image_path}")
        
        # Read image
        image = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to preprocess the image
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        # Apply deskewing
        coords = np.column_stack(np.where(gray > 0))
        angle = cv2.minAreaRect(coords)[-1]
        
        # Rotate the image to deskew
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        logger.info(f"Image preprocessing completed")
        
        return rotated

    def extract_text_with_tesseract(self, image_path: str) -> str:
        """
        Extract text using Tesseract OCR as a fallback
        
        Args:
            image_path (str): Path to input image
        
        Returns:
            Extracted text
        """
        logger.info(f"Attempting Tesseract OCR on: {image_path}")
        
        # Preprocess image
        preprocessed_image = self.preprocess_image(image_path)
        
        # Save preprocessed image for debugging
        preprocessed_path = os.path.join(self.upload_folder, 'preprocessed.jpg')
        cv2.imwrite(preprocessed_path, preprocessed_image)
        logger.info(f"Preprocessed image saved: {preprocessed_path}")
        
        # Extract text with Tesseract
        text = pytesseract.image_to_string(preprocessed_image)
        logger.info(f"Tesseract OCR text length: {len(text)}")
        
        return text

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF using PyPDF2
        
        Args:
            pdf_path (str): Path to PDF file
        
        Returns:
            Extracted text from PDF
        """
        logger.info(f"Extracting text from PDF: {pdf_path}")
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                full_text = ""
                
                for page in reader.pages:
                    full_text += page.extract_text() + "\n"
                
                logger.info(f"PDF text extraction completed. Length: {len(full_text)} characters")
                return full_text
        
        except Exception as e:
            logger.error(f"PDF text extraction failed: {e}")
            return ""

    def analyze_document_with_textract(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze document using AWS Textract with comprehensive logging
        
        Args:
            file_path (str): Path to input document
        
        Returns:
            Comprehensive document analysis
        """
        logger.info(f"Analyzing document: {file_path}")
        
        # Validate file exists
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return {
                'success': False,
                'error': f"File not found: {file_path}"
            }
        
        # Determine file type
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Fallback text extraction for PDFs
        if file_ext == '.pdf':
            full_text = self.extract_text_from_pdf(file_path)
            
            if full_text:
                return {
                    'success': True,
                    'full_text': full_text,
                    'extraction_method': 'PyPDF2'
                }
        
        # Read file bytes
        try:
            with open(file_path, 'rb') as document:
                document_bytes = document.read()
            
            logger.info(f"File read successfully. Size: {len(document_bytes)} bytes")
        except Exception as read_error:
            logger.error(f"Error reading file: {read_error}")
            return {
                'success': False,
                'error': f"Error reading file: {read_error}"
            }
        
        # Validate Textract client
        if self.textract_client is None:
            logger.error("Textract client not initialized")
            return {
                'success': False,
                'error': "AWS Textract client not initialized"
            }
        
        try:
            # Detect document text
            response = self.textract_client.detect_document_text(
                Document={'Bytes': document_bytes}
            )
            
            # Extract text from blocks
            blocks = response.get('Blocks', [])
            full_text = ' '.join([
                block['Text'] 
                for block in blocks 
                if block['BlockType'] == 'LINE'
            ])
            
            logger.info(f"Textract analysis completed. Extracted text length: {len(full_text)}")
            
            return {
                'success': True,
                'full_text': full_text,
                'blocks': blocks,
                'extraction_method': 'Textract'
            }
        
        except Exception as textract_error:
            logger.error(f"Textract analysis failed: {textract_error}")
            
            # Fallback to Tesseract OCR
            try:
                fallback_text = self.extract_text_with_tesseract(file_path)
                logger.info(f"Fallback OCR text length: {len(fallback_text)}")
                
                return {
                    'success': False,
                    'error': str(textract_error),
                    'fallback_text': fallback_text,
                    'extraction_method': 'Tesseract'
                }
            except Exception as ocr_error:
                logger.error(f"Fallback OCR failed: {ocr_error}")
                return {
                    'success': False,
                    'error': f"Textract and OCR failed: {textract_error}, {ocr_error}"
                }

    def parse_bill_details(self, text: str) -> Dict[str, str]:
        """
        Parse bill details using regex and machine learning
        
        Args:
            text (str): Input text from bill
        
        Returns:
            Parsed bill details
        """
        logger.info("Parsing bill details")
        
        details = {}
        
        # Detect bill type (can be enhanced with ML)
        bill_type = 'water_bill'  # Default assumption
        
        if bill_type in self.bill_patterns:
            patterns = self.bill_patterns[bill_type]
            
            for key, pattern_list in patterns.items():
                for pattern in pattern_list:
                    match = re.search(pattern, text, re.IGNORECASE | re.UNICODE)
                    if match:
                        details[key] = match.group(1)
                        break
        
        logger.info(f"Bill details parsed: {details}")
        
        return details

    def generate_bill_insights(self, details: Dict) -> Dict:
        """
        Generate advanced bill insights
        
        Args:
            details (Dict): Parsed bill details
        
        Returns:
            Comprehensive bill insights
        """
        logger.info("Generating bill insights")
        
        insights = {
            'summary': 'Detailed Bill Breakdown',
            'financial_health': {},
            'consumption_analysis': {}
        }
        
        try:
            # Financial Insights
            total_amount = float(details.get('total_amount', 0))
            water_consumption = float(details.get('water_consumption', 0))
            
            insights['financial_health'] = {
                'total_bill': f"{total_amount:.2f} ₺",
                'cost_per_cubic_meter': f"{total_amount / water_consumption:.2f} ₺/m³" if water_consumption > 0 else "N/A"
            }
            
            # Consumption Analysis
            insights['consumption_analysis'] = {
                'total_consumption': f"{water_consumption:.2f} m³",
                'daily_average': f"{water_consumption / 30:.2f} m³/day" if water_consumption > 0 else "N/A"
            }
        
        except Exception as e:
            insights['error'] = str(e)
            logger.error(f"Error generating bill insights: {e}")
        
        logger.info(f"Bill insights generated: {insights}")
        
        return insights

    def process_bill(self, file_path: str) -> Dict:
        """
        Comprehensive bill processing pipeline
        
        Args:
            file_path (str): Path to bill document
        
        Returns:
            Comprehensive bill analysis
        """
        logger.info(f"Processing bill: {file_path}")
        
        # Textract document analysis
        textract_result = self.analyze_document_with_textract(file_path)
        
        if not textract_result.get('success', False):
            return {
                'success': False,
                'error': textract_result.get('error', 'Unknown error'),
                'fallback_text': textract_result.get('fallback_text', '')
            }
        
        # Parse bill details
        bill_details = self.parse_bill_details(textract_result['full_text'])
        
        # Generate insights
        bill_insights = self.generate_bill_insights(bill_details)
        
        logger.info(f"Bill processing completed: {bill_insights}")
        
        return {
            'success': True,
            'textract_result': textract_result,
            'parsed_details': bill_details,
            'bill_insights': bill_insights
        }

    def analyze_water_bill_trends(self, bill_history: List[Dict]) -> Dict:
        """
        Analyze water bill trends over 6 months
        
        Args:
            bill_history (List[Dict]): List of bill details for past 6 months
        
        Returns:
            Comprehensive water consumption and financial insights
        """
        if not bill_history or len(bill_history) < 2:
            return {
                'trend_analysis': 'Insufficient data for trend analysis',
                'recommendations': []
            }
        
        # Extract consumption and financial data
        consumptions = [float(bill.get('water_consumption', 0)) for bill in bill_history]
        total_amounts = [float(bill.get('total_amount', 0)) for bill in bill_history]
        
        # Calculate trends
        avg_consumption = sum(consumptions) / len(consumptions)
        avg_bill_amount = sum(total_amounts) / len(total_amounts)
        
        # Consumption trend
        consumption_trend = 'stable'
        if max(consumptions) > avg_consumption * 1.2:
            consumption_trend = 'increasing'
        elif max(consumptions) < avg_consumption * 0.8:
            consumption_trend = 'decreasing'
        
        # Generate water conservation recommendations
        recommendations = []
        
        if consumption_trend == 'increasing':
            recommendations.extend([
                "🚿 Your water consumption is trending upwards. Consider these water-saving tips:",
                "- Check for and fix any leaks in pipes, faucets, and toilets",
                "- Install water-efficient showerheads and faucet aerators",
                "- Take shorter showers and turn off water while soaping",
                "- Use full loads for washing machines and dishwashers"
            ])
        elif consumption_trend == 'stable':
            recommendations.extend([
                "💧 Your water consumption is consistent. Maintain these good habits:",
                "- Continue monitoring your water usage",
                "- Regularly check for hidden leaks",
                "- Consider a home water audit to identify potential savings"
            ])
        else:
            recommendations.extend([
                "🌿 Great job on reducing water consumption! Keep it up:",
                "- Share your water-saving techniques with family and friends",
                "- Explore additional water conservation methods",
                "- Consider rainwater harvesting or greywater recycling"
            ])
        
        # Financial insights
        financial_recommendations = []
        if avg_bill_amount > 200:  # Adjust threshold as needed
            financial_recommendations.extend([
                "💰 High water bills detected. Financial recommendations:",
                f"- Average monthly water bill: {avg_bill_amount:.2f} TL",
                "- Invest in water-efficient appliances",
                "- Check for potential billing errors",
                "- Explore municipal water-saving incentive programs"
            ])
        
        recommendations.extend(financial_recommendations)
        
        return {
            'trend_analysis': {
                'avg_monthly_consumption': f"{avg_consumption:.2f} m³",
                'consumption_trend': consumption_trend,
                'avg_monthly_bill': f"{avg_bill_amount:.2f} TL"
            },
            'recommendations': recommendations
        }

    def generate_water_conservation_report(self, bill_history: List[Dict]) -> Dict:
        """
        Generate a comprehensive water conservation report
        
        Args:
            bill_history (List[Dict]): List of bill details for past 6 months
        
        Returns:
            Detailed water conservation report
        """
        trend_analysis = self.analyze_water_bill_trends(bill_history)
        
        # Prepare report
        report = {
            'title': '6-Month Water Conservation Analysis',
            'period': f'{bill_history[0].get("billing_period", "N/A")} - {bill_history[-1].get("billing_period", "N/A")}',
            'trend_analysis': trend_analysis['trend_analysis'],
            'recommendations': trend_analysis['recommendations'],
            'actionable_insights': {
                'water_saving_potential': 'Estimated 15-30% reduction possible',
                'environmental_impact': 'Reducing water consumption helps conserve local water resources'
            }
        }
        
        return report

    def process_multiple_bills(self, bill_files: List[str]) -> Dict:
        """
        Process multiple water bills and generate comprehensive report
        
        Args:
            bill_files (List[str]): List of bill file paths
        
        Returns:
            Comprehensive multi-bill analysis
        """
        bill_history = []
        
        for bill_file in bill_files:
            # Analyze individual bill
            bill_result = self.analyze_document_with_textract(bill_file)
            
            if bill_result.get('success', False):
                # Parse bill details
                bill_details = self.parse_bill_details(bill_result['full_text'])
                bill_history.append(bill_details)
        
        # Generate water conservation report
        water_report = self.generate_water_conservation_report(bill_history)
        
        return water_report

    def analyze_bill_details(self, bill_text: str, privacy_mode: bool = False) -> str:
        """
        Analyze bill details with optional privacy protection
        
        Args:
            bill_text (str): Raw text extracted from the bill
            privacy_mode (bool): If True, anonymize sensitive information
        
        Returns:
            str: Detailed bill analysis with optional privacy protection
        """
        try:
            # Basic text preprocessing
            bill_text = bill_text.lower().strip()
            
            # Privacy-aware analysis
            if privacy_mode:
                # Anonymize specific details
                def anonymize(text, pattern, replacement='****'):
                    import re
                    return re.sub(pattern, replacement, text)
                
                # Anonymize potential sensitive information
                bill_text = anonymize(bill_text, r'\d{10,}')  # Long number sequences
                bill_text = anonymize(bill_text, r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')  # Email
                bill_text = anonymize(bill_text, r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')  # Phone numbers
            
            # Intelligent analysis
            insights = []
            
            # Detect bill type
            if 'water' in bill_text or 'su faturası' in bill_text:
                insights.append("📊 Water Bill Detected")
            
            # Consumption analysis
            if 'tüketim' in bill_text or 'consumption' in bill_text:
                insights.append("💧 Consumption Detected: Analyzing water usage patterns")
            
            # Financial insights
            if 'toplam tutar' in bill_text or 'total amount' in bill_text:
                insights.append("💰 Financial Summary: Identifying key payment details")
            
            # Formatting the response
            response = "🕵️ Confidential Bill Insights:\n\n"
            response += "\n".join(insights)
            response += "\n\n🔒 Sensitive details have been protected for your privacy."
            
            return response
        
        except Exception as e:
            logger.error(f"Bill details analysis error: {str(e)}")
            return "Unable to process bill details at this time."

    def process_bill_with_advanced_analysis(self, bill_text: str) -> Dict[str, Any]:
        """
        Process bill text with advanced analysis and structured output
        
        Args:
            bill_text (str): Raw bill text
        
        Returns:
            Comprehensive bill analysis dictionary
        """
        logger.info("Starting bill analysis")
        logger.debug(f"Input bill text: {bill_text}")

        try:
            # Comprehensive regex patterns for bill details
            patterns = {
                'bill_number': [
                    r'FATURA NO[:]*\s*(\d+)', 
                    r'Invoice Number[:]*\s*(\d+)'
                ],
                'subscriber_number': [
                    r'ABONE NO[:]*\s*(\d+)', 
                    r'Subscriber Number[:]*\s*(\d+)'
                ],
                'billing_period': [
                    r'DÖNEM[:]*\s*(\d{4}-\d{2})', 
                    r'Billing Period[:]*\s*(\d{4}-\d{2})'
                ],
                'total_consumption': [
                    r'TÜKETIM \(m3\)[:]*\s*(\d+(?:\.\d+)?)', 
                    r'Consumption \(m3\)[:]*\s*(\d+(?:\.\d+)?)'
                ],
                'water_cost': [
                    r'SU BEDELİ \(TL\)[:]*\s*(\d+(?:\.\d+)?)', 
                    r'Water Cost \(TL\)[:]*\s*(\d+(?:\.\d+)?)'
                ],
                'wastewater_cost': [
                    r'ATIKSU BEDELİ \(TL\)[:]*\s*(\d+(?:\.\d+)?)', 
                    r'Wastewater Cost \(TL\)[:]*\s*(\d+(?:\.\d+)?)'
                ],
                'total_bill': [
                    r'TOPLAM BORC \(TL\)[:]*\s*(\d+(?:\.\d+)?)', 
                    r'Total Bill \(TL\)[:]*\s*(\d+(?:\.\d+)?)'
                ],
                'reading_days': [
                    r'OKUMA GÜN SAYISI[:]*\s*(\d+)', 
                    r'Reading Days[:]*\s*(\d+)'
                ]
            }

            # Function to safely extract first match from multiple patterns
            def safe_extract(key, default='N/A'):
                for pattern in patterns[key]:
                    matches = re.findall(pattern, bill_text, re.IGNORECASE)
                    if matches:
                        logger.info(f"Found {key} using pattern: {pattern}")
                        return matches[0]
                logger.warning(f"No match found for {key}")
                return default

            # Extract bill details
            bill_details = {
                key: safe_extract(key) for key in patterns.keys()
            }

            # Convert numeric values safely
            def safe_float(value, default=0.0):
                try:
                    return float(value) if value != 'N/A' else default
                except ValueError:
                    logger.error(f"Could not convert {value} to float")
                    return default

            # Compute metrics
            total_consumption = safe_float(bill_details['total_consumption'])
            water_cost = safe_float(bill_details['water_cost'])
            wastewater_cost = safe_float(bill_details['wastewater_cost'])
            total_bill = safe_float(bill_details['total_bill'])
            reading_days = re.findall(r'OKUMA GÜN SAYISI[:]*\s*(\d+)', bill_text)
            reading_days = int(safe_float(bill_details['reading_days'], default=1))

            # Prevent division by zero
            cost_per_cubic_meter = water_cost / total_consumption if total_consumption > 0 else 0
            daily_average = total_consumption / reading_days if reading_days > 0 else 0

            # Structured analysis output
            analysisOutput = f"""Bill Analysis 1 Successfully Processed
Bill Details
- Bill Number: {bill_details['bill_number']}
- Billing Period: {bill_details['billing_period']}
- Subscriber Number: {bill_details['subscriber_number']}

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

            logger.info("Bill analysis completed successfully")

            return {
                'raw_text': bill_text,
                'analysisOutput': analysisOutput,
                'details': {
                    'bill_number': bill_details['bill_number'],
                    'billing_period': bill_details['billing_period'],
                    'total_consumption': total_consumption,
                    'total_bill': total_bill,
                    'water_cost': water_cost,
                    'wastewater_cost': wastewater_cost,
                    'cost_per_cubic_meter': cost_per_cubic_meter,
                    'daily_average': daily_average
                }
            }

        except Exception as e:
            logger.error(f"Comprehensive bill analysis failed: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            return {
                'raw_text': bill_text,
                'analysisOutput': """Bill Analysis Failed
Unable to process bill details.
Please check the input text and try again.""",
                'error': str(e)
            }

def analyze_bill(file_path: str, log_level=logging.INFO) -> Dict:
    """
    Convenient function to analyze a bill with configurable logging
    
    Args:
        file_path (str): Path to bill document
        log_level (int): Logging level
    
    Returns:
        Comprehensive bill analysis
    """
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bill_analysis.log', mode='a', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger('IntelligentBillAnalyzer')
    
    try:
        # Validate file path
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return {
                'success': False,
                'error': f"File not found: {file_path}"
            }
        
        # Log file details
        file_stats = os.stat(file_path)
        logger.info(f"Analyzing file: {file_path}")
        logger.info(f"File size: {file_stats.st_size} bytes")
        logger.info(f"File extension: {os.path.splitext(file_path)[1]}")
        
        # Initialize analyzer
        analyzer = IntelligentBillAnalyzer()
        
        # Analyze document
        result = analyzer.process_bill(file_path)
        
        # Additional logging
        if result.get('success', False):
            logger.info("Bill analysis completed successfully")
        else:
            logger.warning(f"Bill analysis failed: {result.get('error', 'Unknown error')}")
        
        return result
    
    except Exception as e:
        # Comprehensive error handling
        logger.error(f"Unexpected error during bill analysis: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}"
        }

# Supported file types
SUPPORTED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.tiff'}

def is_supported_file(filename: str) -> bool:
    """
    Check if file type is supported
    
    Args:
        filename (str): Name of the file
    
    Returns:
        Boolean indicating file support
    """
    return os.path.splitext(filename)[1].lower() in SUPPORTED_EXTENSIONS
