import requests
from flask import Blueprint, jsonify, request
import logging
import json

weather_bp = Blueprint('weather', __name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@weather_bp.route('/get-weather')
def get_weather():
    try:
        # Try multiple location services
        location_services = [
            ('ipapi.co', 'https://ipapi.co/json/'),
            ('ip-api.com', 'http://ip-api.com/json/'),
        ]
        
        location_data = None
        for service_name, url in location_services:
            try:
                response = requests.get(url, timeout=5)
                location_data = response.json()
                
                # Log raw location data
                logger.debug(f"Location data from {service_name}: {json.dumps(location_data, indent=2)}")
                
                # Validate location data
                city = location_data.get('city')
                country = location_data.get('country_name') or location_data.get('country')
                latitude = location_data.get('latitude') or location_data.get('lat')
                longitude = location_data.get('longitude') or location_data.get('lon')
                
                # Check if we have valid location data
                if all([city, country, latitude, longitude]):
                    break
                
                logger.warning(f"Incomplete location data from {service_name}")
            except Exception as e:
                logger.error(f"Error fetching location from {service_name}: {e}")
        
        # If no valid location data found
        if not location_data or not all([city, country, latitude, longitude]):
            logger.error("Could not retrieve location from any service")
            return jsonify({
                'error': 'Unable to determine location',
                'details': 'No valid location data found',
                'raw_data': location_data
            }), 400
        
        # Fetch weather data from Open Meteo
        try:
            weather_url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,windspeed_10m,cloudcover'
            weather_response = requests.get(weather_url, timeout=10)
            
            # Check if weather request was successful
            if weather_response.status_code != 200:
                logger.error(f"Weather API request failed: {weather_response.status_code}")
                return jsonify({
                    'error': 'Unable to fetch weather data',
                    'details': 'Weather service unavailable'
                }), 500
            
            weather_data = weather_response.json()
            
            # Extract current weather information
            current_weather = weather_data['current_weather']
            
            # Get the current hour index
            current_hour_index = 0  # Assuming the first hour is current
            
            return jsonify({
                'location': f"{city}, {country}",
                'temperature': current_weather['temperature'],
                'wind_speed': current_weather['windspeed'],
                'wind_direction': current_weather['winddirection'],
                'humidity': weather_data['hourly']['relativehumidity_2m'][current_hour_index],
                'cloudiness': weather_data['hourly']['cloudcover'][current_hour_index],
                'latitude': latitude,
                'longitude': longitude
            })
        
        except Exception as weather_error:
            logger.error(f"Weather data fetch error: {weather_error}")
            return jsonify({
                'error': 'Weather data retrieval failed',
                'details': str(weather_error)
            }), 500
    
    except Exception as e:
        logger.error(f"Unexpected error in get_weather: {e}")
        return jsonify({
            'error': 'Unexpected error',
            'details': str(e)
        }), 500
