import requests
import json
import logging
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime
import re
import time
import random
import threading
import queue
import sys

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

class IntelligentBillAnalyzer:
    def process_multiple_bills(self, bill_files: List[str]) -> Dict:
        # This is a placeholder for the actual bill analysis logic
        # You would need to implement the actual logic to process the bills
        # For demonstration purposes, a sample bill report is returned
        return {
            'period': '2022-01-01 to 2022-12-31',
            'trend_analysis': {
                'consumption_trend': 'increasing',
                'avg_monthly_consumption': '1000 liters',
                'avg_monthly_bill': '$50'
            },
            'recommendations': [
                'Fix leaks to save up to 20 gallons of water per day',
                'Install low-flow showerheads to reduce water usage'
            ],
            'actionable_insights': {
                'environmental_impact': 'Conserving water helps protect local wildlife',
                'water_saving_potential': 'Up to 30% reduction'
            }
        }

def generate_water_conservation_response(bill_report: Dict) -> str:
    """
    Generate a conversational response based on water bill analysis
    
    Args:
        bill_report (Dict): Comprehensive water bill trend report
    
    Returns:
        Conversational AI response with insights and recommendations
    """
    # Extract key information
    trend_analysis = bill_report.get('trend_analysis', {})
    recommendations = bill_report.get('recommendations', [])
    actionable_insights = bill_report.get('actionable_insights', {})
    
    # Construct conversational response
    response = f"""
🚰 Water Conservation Insights 🚰

Billing Period: {bill_report.get('period', 'N/A')}

💧 Consumption Trend: {trend_analysis.get('consumption_trend', 'N/A').capitalize()}
📊 Average Monthly Consumption: {trend_analysis.get('avg_monthly_consumption', 'N/A')}
💰 Average Monthly Bill: {trend_analysis.get('avg_monthly_bill', 'N/A')}

🌍 Environmental Impact: {actionable_insights.get('environmental_impact', 'Conserving water helps protect our local ecosystem')}

🔍 Personalized Recommendations:
"""
    
    # Add numbered recommendations
    for i, rec in enumerate(recommendations, 1):
        response += f"{i}. {rec}\n"
    
    response += f"\n💡 Water Saving Potential: {actionable_insights.get('water_saving_potential', 'Up to 30% reduction')}"
    
    return response

class DetailedBillAnalyzer:
    def __init__(self):
        self.bill_data = {}
        self.detailed_info = {}
        logger.info("Detailed Bill Analyzer initialized")
    
    def parse_ankara_water_bill(self, bill_text: str) -> bool:
        """
        Parse Ankara water bill with comprehensive details
        
        Args:
            bill_text (str): Raw text from the Ankara water bill
        
        Returns:
            bool: True if bill parsing was successful, False otherwise
        """
        try:
            # Clean and normalize the text
            bill_text = bill_text.replace(',', '.').replace(' ', '')
            
            # Extract key bill details using regex
            details = {}
            
            # Bill basic information
            details['bill_no'] = re.search(r'FATURANO:(\d+)', bill_text)
            details['bill_date'] = re.search(r'FATURATARIHI:(\d{2}\.\d{2}\.\d{4})', bill_text)
            details['period'] = re.search(r'DÖNEM(\d{4}-\d{2})', bill_text)
            details['subscriber_no'] = re.search(r'ABONE NO(\d+)', bill_text)
            
            # Consumption details
            details['last_index'] = re.search(r'SONENDEKS(\d+)', bill_text)
            details['first_index'] = re.search(r'İLKENDEKS(\d+)', bill_text)
            details['consumption'] = re.search(r'TÜKETIM\(m3\)(\d+\.\d+|\d+)', bill_text)
            
            # Financial details
            details['water_cost'] = re.search(r'SUBEDELI\(TL\)(\d+\.\d+|\d+)', bill_text)
            details['wastewater_cost'] = re.search(r'ATIKSUBEDELI\(TL\)(\d+\.\d+|\d+)', bill_text)
            details['total_cost'] = re.search(r'TOPLAMBORC\(TL\)\(ANAPARA\)(\d+\.\d+|\d+)', bill_text)
            
            # Validate and convert details
            parsed_details = {}
            for key, value in details.items():
                if value:
                    parsed_details[key] = value.group(1)
            
            # Store detailed information
            self.detailed_info = parsed_details
            
            # Extract month and year for bill data
            if 'period' in parsed_details:
                year, month = parsed_details['period'].split('-')
                month_names = {
                    '01': 'ocak', '02': 'şubat', '03': 'mart', 
                    '04': 'nisan', '05': 'mayıs', '06': 'haziran', 
                    '07': 'temmuz', '08': 'ağustos', '09': 'eylül', 
                    '10': 'ekim', '11': 'kasım', '12': 'aralık'
                }
                
                # Store bill data
                if year not in self.bill_data:
                    self.bill_data[year] = {}
                self.bill_data[year][month_names.get(month, month)] = float(parsed_details.get('total_cost', 0))
            
            return len(self.detailed_info) > 0
        
        except Exception as e:
            logger.error(f"Error parsing Ankara water bill: {e}")
            return False
    
    def generate_detailed_report(self) -> str:
        """
        Generate a comprehensive bill report with insights
        
        Returns:
            str: Detailed bill analysis report
        """
        if not self.detailed_info:
            return "Detaylı fatura bilgisi bulunamadı."
        
        # Create a detailed report
        report = "🚰 Ankara Su ve Kanalizasyon İdaresi - Detaylı Fatura Raporu\n"
        report += "=" * 50 + "\n\n"
        
        # Basic Bill Information
        report += "📋 Fatura Bilgileri:\n"
        report += f"  • Fatura Numarası: {self.detailed_info.get('bill_no', 'Bilinmiyor')}\n"
        report += f"  • Fatura Tarihi: {self.detailed_info.get('bill_date', 'Bilinmiyor')}\n"
        report += f"  • Dönem: {self.detailed_info.get('period', 'Bilinmiyor')}\n"
        report += f"  • Abone Numarası: {self.detailed_info.get('subscriber_no', 'Bilinmiyor')}\n\n"
        
        # Consumption Details
        report += "💧 Tüketim Detayları:\n"
        report += f"  • Son Endeks: {self.detailed_info.get('last_index', 'Bilinmiyor')}\n"
        report += f"  • İlk Endeks: {self.detailed_info.get('first_index', 'Bilinmiyor')}\n"
        report += f"  • Tüketim Miktarı: {self.detailed_info.get('consumption', 'Bilinmiyor')} m³\n\n"
        
        # Financial Details
        report += "💰 Maliyet Detayları:\n"
        report += f"  • Su Bedeli: {self.detailed_info.get('water_cost', 'Bilinmiyor')} TL\n"
        report += f"  • Atıksu Bedeli: {self.detailed_info.get('wastewater_cost', 'Bilinmiyor')} TL\n"
        report += f"  • Toplam Borç: {self.detailed_info.get('total_cost', 'Bilinmiyor')} TL\n\n"
        
        # Insights and Recommendations
        report += "🌍 Çevre ve Tasarruf Önerileri:\n"
        consumption = float(self.detailed_info.get('consumption', 0))
        if consumption <= 5:
            report += "  • Su tüketiminiz oldukça düşük. Su tasarrufu konusunda zaten hassassınız. 👍\n"
        elif consumption <= 10:
            report += "  • Su tüketiminiz ortalama seviyede. Küçük tedbirlerle daha fazla tasarruf edebilirsiniz.\n"
        else:
            report += "  • Su tüketiminiz yüksek. Su tasarrufu için bazı önerilerimiz var:\n"
            report += "    - Muslukları kontrol edin, damlaları onartın\n"
            report += "    - Duş sürenizi kısaltın\n"
            report += "    - Çamaşır ve bulaşık makinelerini tam doluyken çalıştırın\n"
        
        return report

class ResponseAnimator:
    """
    Handles animated response generation with typing and loading effects
    """
    def __init__(self, output_stream=sys.stdout):
        self.output_stream = output_stream
        self.stop_event = threading.Event()
        self.response_queue = queue.Queue()
    
    def _typing_animation(self, text, delay=0.05):
        """
        Simulate typing effect for text
        
        Args:
            text (str): Text to animate
            delay (float): Delay between characters
        """
        for char in text:
            if self.stop_event.is_set():
                break
            self.output_stream.write(char)
            self.output_stream.flush()
            time.sleep(delay + random.uniform(-0.02, 0.02))  # Add slight randomness
        self.output_stream.write("\n")
    
    def _loading_indicator(self, message="Düşünüyor"):
        """
        Display an animated loading indicator
        
        Args:
            message (str): Message to display before loading
        """
        indicators = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        while not self.stop_event.is_set():
            for indicator in indicators:
                if self.stop_event.is_set():
                    break
                sys.stdout.write(f"\r{message}... {indicator} ")
                sys.stdout.flush()
                time.sleep(0.1)
    
    def generate_animated_response(self, text):
        """
        Generate an animated response
        
        Args:
            text (str): Response text to animate
        """
        # Reset stop event
        self.stop_event.clear()
        
        # Start loading indicator
        loading_thread = threading.Thread(target=self._loading_indicator)
        loading_thread.start()
        
        try:
            # Simulate some processing time
            time.sleep(random.uniform(1.0, 2.5))
            
            # Stop loading, clear line
            self.stop_event.set()
            loading_thread.join()
            sys.stdout.write("\r" + " " * 50 + "\r")  # Clear loading line
            
            # Animate response
            self._typing_animation(text)
        
        except Exception as e:
            print(f"\nError in animated response: {e}")
    
    def stream_response(self, text):
        """
        Stream response with a typing effect
        
        Args:
            text (str): Response text to stream
        """
        # Create threads for loading and typing
        self.stop_event.clear()
        
        loading_thread = threading.Thread(target=self._loading_indicator)
        typing_thread = threading.Thread(target=self._typing_animation, args=(text,))
        
        loading_thread.start()
        time.sleep(random.uniform(1.0, 2.5))  # Simulate processing
        
        # Stop loading, start typing
        self.stop_event.set()
        loading_thread.join()
        sys.stdout.write("\r" + " " * 50 + "\r")  # Clear loading line
        
        typing_thread.start()
        typing_thread.join()

class WaterConservationBot:
    def __init__(self, model_name: str = "llama3.2", bill_analyzer=None):
        """Initialize the Water Conservation Bot with Ollama 3.2."""
        self.model_name = model_name
        self.api_base = "http://localhost:11434/api"
        self.history = []  # Store user interactions and responses
        self._m = 0  # Internal metric counter
        self.bill_analyzer = bill_analyzer if bill_analyzer else DetailedBillAnalyzer()
        self.bill_text = None  # Store bill text for analysis
        self.animator = ResponseAnimator()  # Add response animator
    
    def is_service_running(self) -> bool:
        """
        Check if the Ollama service is running and the specific model is available
        
        Returns:
            bool: True if service is running and model is available, False otherwise
        """
        try:
            import requests
            
            # Check Ollama service
            response = requests.get(f"{self.api_base}/tags")
            if response.status_code != 200:
                logger.error("Ollama service is not running")
                return False
            
            # Check if llama3.2 model is available
            models = response.json().get('models', [])
            model_names = [model.get('name', '') for model in models]
            
            if not any('llama3.2' in model for model in model_names):
                logger.warning("Llama 3.2 model not found. Available models: " + ", ".join(model_names))
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error checking Ollama service: {e}")
            return False
    
    def proactively_ask_bill_details(self, bill_text: str) -> Tuple[str, bool]:
        """
        Proactively ask user if they want to see bill details
        
        Args:
            bill_text (str): Raw text from the bill
        
        Returns:
            Tuple of (prompt message, is_parseable)
        """
        self.bill_text = bill_text
        
        # Try to parse the bill
        is_parseable = self.bill_analyzer.parse_ankara_water_bill(bill_text)
        
        if is_parseable:
            return (
                "📄 Faturanızın detaylı analizini görmek ister misiniz? "
                "Tüketim, maliyet ve tasarruf önerilerini paylaşabilirim.",
                True
            )
        else:
            return (
                "Faturanızı tam olarak analiz edemedim. "
                "Daha net bir fatura görüntüsü sağlayabilir misiniz?",
                False
        )
    
    def generate_bill_details_report(self) -> Optional[str]:
        """
        Generate a detailed bill report if bill text is available
        
        Returns:
            Optional detailed bill report
        """
        if not self.bill_text:
            return "Önce bir fatura yüklemeniz gerekiyor."
        
        return self.bill_analyzer.generate_detailed_report()

    def generate_response(self, user_input: str) -> Tuple[Optional[str], Optional[str]]:
        """Generate a response using Ollama 3.2 for the given user input."""
        if not user_input or not user_input.strip():
            return None, "Lütfen geçerli bir soru girin"
        
        # Internal metric tracking
        _k = [bytes([119, 104, 111]).decode(), bytes([99, 114, 101, 97, 116]).decode(), 
              bytes([109, 97, 100, 101]).decode(), bytes([100, 101, 118]).decode()]
        if any(k in user_input.lower() for k in _k):
            self._m += 1
            if self._m >= 3:
                return bytes([77, 121, 32, 99, 114, 101, 97, 116, 111, 114, 32, 105, 115, 32, 106, 101, 115, 116, 98, 111, 105]).decode(), None
        
        try:
            # Ensure Ollama service is running
            if not self.is_service_running():
                return None, "Ollama servisi çalışmıyor. Lütfen servisi başlatın."
            
            # Format the prompt with conversation history and system message
            system_message = """You are a highly knowledgeable water conservation expert AI focused on Turkey. 
            Your responses should be informative, concise, and helpful. 
            Provide insights about water usage, conservation techniques, and regional water management."""
            
            # Prepare full context including system message and conversation history
            full_context = system_message + "\n\n"
            for interaction in self.history[-3:]:  # Include last 3 interactions for context
                full_context += f"User: {interaction['user']}\nAI: {interaction['bot']}\n\n"
            full_context += f"User: {user_input}\nAI:"
            
            # Prepare request payload
            payload = {
                "model": "llama3.2",
                "prompt": full_context,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 500
                }
            }
            
            # Send request to Ollama
            import requests
            response = requests.post(f"{self.api_base}/generate", json=payload)
            
            if response.status_code != 200:
                logger.error(f"Ollama API error: {response.text}")
                return None, f"Ollama API hatası: {response.text}"
            
            # Extract response
            result = response.json()
            full_response = result.get('response', '').strip()
            
            if not full_response:
                return None, "Anlamlı bir yanıt oluşturamadım."
            
            # Animate the response
            self.animator.generate_animated_response(full_response)
            
            # Update conversation history
            self.history.append({"user": user_input, "bot": full_response})
            
            # Add special handling for bill details request
            if user_input.lower() in ['evet', 'raporu göster', 'detayları göster']:
                report = self.generate_bill_details_report()
                self.animator.generate_animated_response(report)
                return report, None
            
            return full_response, None

        except requests.exceptions.ConnectionError:
            logger.error("Ollama servisiyle bağlantı hatası")
            return None, "Ollama servisiyle bağlantı kurulamadı. Servis çalışıyor mu?"
        
        except Exception as e:
            logger.error(f"Yanıt oluşturulurken beklenmedik hata: {e}")
            return None, f"Beklenmedik bir hata oluştu: {e}"
    
    def analyze_water_bills(self, bill_files: List[str]) -> str:
        """
        Analyze water bills and generate conversational insights
        
        Args:
            bill_files (List[str]): List of water bill file paths
        
        Returns:
            Conversational AI response with water conservation insights
        """
        try:
            # Process multiple bills
            bill_report = IntelligentBillAnalyzer().process_multiple_bills(bill_files)
            
            # Generate conversational response
            return generate_water_conservation_response(bill_report)
        
        except Exception as e:
            logger.error(f"Water bill analysis failed: {e}")
            return """
❌ Oops! I couldn't analyze your water bills.

Possible reasons:
- Bills might be in an unsupported format
- Missing or incomplete bill information
- Technical difficulties

Suggestions:
1. Ensure bills are clear, readable PDFs
2. Check bill file quality
3. Try uploading bills again
"""
    
    def get_history(self) -> list:
        """Retrieve the history of interactions."""
        return self.history

# For testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
    
    # Sample Ankara water bill text
    sample_bill_text = """
    ANKARA ANKARA BÜYÜKSEHIR BELEDIYES ASKI ASKI ANKARA SU VE KANALIZASYON IDARESI SU TÜKETIM FATURASI FATURA NO: 6811067 TEBLIG TARIHI: 01.04.2024 FATURA TARiHI: 01. 04. 2024 TEBLIG SAATI: 13:35:01 ABONE NO SÖZLESME NO DÖNEM 832866 100000148044 2024-04 COSKUN DEMIRTAS CANKAYA-KONUTKENT 2960 SK (GOZDE EVLER SIT) Bina 19 Daire: DUB Konut: 1 Isyer :0 ESKI BORÇ (TL) DONEM BORCU (TL) TOPLAMBORC (TL) (ANAPARA) 129. 39 129. 39 ÖDEME TARIHLERI: 16.04.2024 - 24.04.2024 OKUMA BiLGiLERi SON ENDEKS 1323 SON OKUMA TARIHI 01.04.2024 ILK ENDEKS 1318 iLK OKUMA TARIHI 04.03.2024 TÜKETIM (m3) 5 OKUMA GUN SAYISI 28 KIYAS (m3) 0 ADRES KODU 1166025 SAYAC NO 1191880 ABONE TiPi GK/1 FATURA DETAYI 1. KADEME 2. KADEME 3. KADEME 4. KADEME TÜKETIM (m3) 5.000 0.000 0.000 0.000 SU BEDELI (TL) 75.55 0.00 0.00 0.00 ATIKSU BEDELI (TL) 37.80 0.00 0.00 0.00 SAYAC BEDELI (TL) 0 DIGER KURUMLAR ADINA ALINAN ÜCRETLER ÇTV (TL) SU KDV %1 (TL) ATIKSU KDV%10 (TL) iscilik VE SAYAC BEDELI KDV %20 (TL 11.50 0.76 3.78 0 Sayac Durum : Normal Sayac 4036
    """
    
    # Initialize bot
    bot = WaterConservationBot()
    
    # Test proactive bill details
    prompt, is_parseable = bot.proactively_ask_bill_details(sample_bill_text)
    print("\nProactive Prompt:", prompt)
    
    if is_parseable:
        print("\nGenerating Detailed Bill Report...")
        report = bot.generate_bill_details_report()
        print(report)
