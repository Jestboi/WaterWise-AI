import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import math

# Load .env file
load_dotenv()

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculates the distance between two points in kilometers."""
    R = 6371  # Earth's radius (km)
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2) * math.sin(delta_lat/2) + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * \
        math.sin(delta_lon/2) * math.sin(delta_lon/2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance

class WeatherService:
    def __init__(self):
        self.weather_url = "https://api.open-meteo.com/v1/forecast"
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
        
    def get_location_details(self, lat, lon):
        """Gets address details from coordinates."""
        try:
            params = {
                'latitude': lat,
                'longitude': lon,
                'language': 'en'  
            }
            
            response = requests.get("https://api.bigdatacloud.net/data/reverse-geocode-client", params=params)
            response.raise_for_status()
            
            data = response.json()
            address = {
                'city': data.get('principalSubdivision', ''),  
                'district': data.get('locality', ''),  
                'country': data.get('countryName', '')  
            }
            
            return address
            
        except Exception as e:
            print(f"Could not get location details: {str(e)}")
            return None
        
    def get_weather_description(self, weathercode):
        """Converts weather code to English description."""
        weather_codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Dense fog",
            51: "Light drizzle",
            53: "Drizzle",
            55: "Dense drizzle",
            61: "Light rain",
            63: "Rain",
            65: "Heavy rain",
            71: "Light snow",
            73: "Snow",
            75: "Heavy snow",
            77: "Snow grains",
            80: "Light rain showers",
            81: "Rain showers",
            82: "Heavy rain showers",
            85: "Light snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with hail",
            99: "Thunderstorm with heavy hail"
        }
        return weather_codes.get(weathercode, "Unknown weather")
        
    def get_weather_advice(self, temperature, description):
        """Generate advice based on weather conditions."""
        if temperature > 30:
            return "High temperature. Water conservation is crucial. Water early morning or late evening."
        elif temperature < 10:
            return "Low temperature. Minimal water evaporation expected."
        elif 'rain' in description.lower():
            return "Rain expected. No immediate irrigation needed."
        elif 'cloudy' in description.lower():
            return "Moderate conditions. Follow standard water conservation practices."
        else:
            return "Good conditions for water conservation activities."
        
    def get_weather(self, lat=None, lon=None):
        """Gets weather information for the specified coordinates."""
        try:
            # Use Istanbul as default if no location provided
            if lat is None or lon is None:
                lat = 41.0082
                lon = 28.9784  
                location_details = {
                    'city': 'Istanbul',
                    'district': 'Center',
                    'country': 'Turkey'
                }
            else:
                location_details = self.get_location_details(lat, lon)
            
            params = {
                'latitude': lat,
                'longitude': lon,
                'current': 'temperature_2m,weathercode',
                'timezone': 'auto'
            }
            
            response = requests.get(self.weather_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract current weather details
            current_weather = data.get('current', {})
            temperature = current_weather.get('temperature_2m', 0)
            weathercode = current_weather.get('weathercode', 0)
            
            # Get weather description
            description = self.get_weather_description(weathercode)
            
            # Determine advice based on weather
            advice = self.get_weather_advice(temperature, description)
            
            return {
                'location': location_details,
                'description': description,
                'temperature': temperature,
                'advice': advice
            }
        
        except Exception as e:
            print(f"Weather service error: {str(e)}")
            raise
        
class WaterOutageService:
    def __init__(self):
        self.api_key = os.getenv('ISKI_API_KEY')
        self.api_url = os.getenv('ISKI_API_URL')
        
        # Example data - in a real application, this would come from a database or API
        self.districts = [
            {'name': 'Kadıköy', 'lat': 40.9927, 'lon': 29.0277},
            {'name': 'Beşiktaş', 'lat': 41.0422, 'lon': 29.0083},
            {'name': 'Üsküdar', 'lat': 41.0234, 'lon': 29.0152},
            {'name': 'Şişli', 'lat': 41.0602, 'lon': 28.9877},
            {'name': 'Maltepe', 'lat': 40.9351, 'lon': 29.1307}
        ]
    
    def get_outages(self, lat=None, lon=None):
        """Gets water outage information for the nearest district."""
        try:
            # If location is provided, find the nearest district
            nearest_district = None
            if lat is not None and lon is not None:
                min_distance = float('inf')
                for district in self.districts:
                    distance = calculate_distance(
                        float(lat), float(lon),
                        district['lat'], district['lon']
                    )
                    if distance < min_distance:
                        min_distance = distance
                        nearest_district = district
            
            # Example outage data - in a real application, this would come from an API
            example_outages = []
            
            if nearest_district:
                # Outage information for the nearest district
                if nearest_district['name'] == 'Kadıköy':
                    example_outages.append({
                        'district': 'Kadıköy',
                        'start_time': '2024-12-28 10:00',
                        'end_time': '2024-12-28 16:00',
                        'reason': 'Scheduled maintenance'
                    })
                elif nearest_district['name'] == 'Beşiktaş':
                    example_outages.append({
                        'district': 'Beşiktaş',
                        'start_time': '2024-12-29 09:00',
                        'end_time': '2024-12-29 15:00',
                        'reason': 'Infrastructure work'
                    })
            else:
                # Default to showing all outages
                example_outages = [
                    {
                        'district': 'Kadıköy',
                        'start_time': '2024-12-28 10:00',
                        'end_time': '2024-12-28 16:00',
                        'reason': 'Scheduled maintenance'
                    },
                    {
                        'district': 'Beşiktaş',
                        'start_time': '2024-12-29 09:00',
                        'end_time': '2024-12-29 15:00',
                        'reason': 'Infrastructure work'
                    }
                ]
            
            return {
                'success': True,
                'outages': example_outages,
                'nearest_district': nearest_district['name'] if nearest_district else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
