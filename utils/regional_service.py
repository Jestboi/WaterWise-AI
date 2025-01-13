import requests
from datetime import datetime
import json
import os

class RegionalService:
    def __init__(self):
        # API anahtarlarını güvenli bir şekilde yükleyin
        self.weather_api_key = os.getenv('WEATHER_API_KEY', 'your_weather_api_key')
        self.dam_api_key = os.getenv('DAM_API_KEY', 'your_dam_api_key')
        
    def get_weather_recommendation(self, lat, lon):
        """Hava durumu verilerine göre sulama tavsiyesi oluşturur"""
        try:
            # OpenWeatherMap API'den hava durumu verilerini al
            url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={self.weather_api_key}&units=metric"
            response = requests.get(url)
            data = response.json()
            
            if response.status_code == 200:
                # Önümüzdeki 24 saat için yağış kontrolü
                next_24h = data['list'][:8]  # 3 saatlik aralıklarla 24 saat
                rain_expected = any('rain' in period for period in next_24h)
                temp = next_24h[0]['main']['temp']
                humidity = next_24h[0]['main']['humidity']
                
                # Sulama tavsiyesi oluştur
                if rain_expected:
                    return {
                        "recommendation": "Irrigation not recommended. Rain expected in the next 24 hours.",
                        "details": {
                            "temperature": temp,
                            "humidity": humidity,
                            "rain_forecast": True
                        }
                    }
                elif temp > 30:
                    return {
                        "recommendation": "Early morning or evening irrigation recommended due to high temperature.",
                        "details": {
                            "temperature": temp,
                            "humidity": humidity,
                            "rain_forecast": False
                        }
                    }
                else:
                    return {
                        "recommendation": "Normal irrigation schedule can be followed.",
                        "details": {
                            "temperature": temp,
                            "humidity": humidity,
                            "rain_forecast": False
                        }
                    }
        except Exception as e:
            return {
                "error": str(e),
                "recommendation": "Unable to fetch weather data. Please check manually."
            }

    def get_dam_status(self, region_id):
        """Baraj doluluk oranlarını getirir"""
        try:
            # Örnek veri - Gerçek API'ye bağlanılmalı
            # Bu kısım sizin kullandığınız API'ye göre değiştirilmeli
            dummy_data = {
                "ankara": {
                    "capacity": 85,
                    "trend": "stable",
                    "last_updated": datetime.now().isoformat()
                },
                "istanbul": {
                    "capacity": 70,
                    "trend": "decreasing",
                    "last_updated": datetime.now().isoformat()
                }
            }
            
            if region_id in dummy_data:
                return {
                    "status": "success",
                    "data": dummy_data[region_id]
                }
            else:
                return {
                    "status": "error",
                    "message": "Region not found"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def get_regional_insights(self, lat, lon, region_id):
        """Tüm bölgesel içgörüleri bir arada getirir"""
        weather_data = self.get_weather_recommendation(lat, lon)
        dam_data = self.get_dam_status(region_id)
        
        return {
            "weather": weather_data,
            "dam": dam_data,
            "timestamp": datetime.now().isoformat()
        }
