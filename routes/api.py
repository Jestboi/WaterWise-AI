from flask import jsonify, request
from utils.weather_service import WeatherService, WaterOutageService

weather_service = WeatherService()
outage_service = WaterOutageService()

def init_api_routes(app):
    @app.route('/api/weather')
    def get_weather():
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        result = weather_service.get_weather(lat=lat, lon=lon)
        return jsonify(result)
    
    @app.route('/api/water-outages')
    def get_water_outages():
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        result = outage_service.get_outages(lat=lat, lon=lon)
        return jsonify(result)
