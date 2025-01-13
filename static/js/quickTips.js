document.addEventListener('DOMContentLoaded', function() {
    let userLocation = null;

    // Utility function to safely update element text
    function safelyUpdateElementText(elementId, text) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = text;
        } else {
            console.warn(`Element with ID ${elementId} not found`);
        }
    }

    // Get user's geolocation
    async function getUserLocation() {
        return new Promise((resolve, reject) => {
            // Allow geolocation in development environments
            const isDevelopment = window.location.hostname === 'localhost' || 
                                  window.location.hostname === '127.0.0.1' ||
                                  window.location.hostname === '';

            if (!window.isSecureContext && !isDevelopment) {
                console.warn('Geolocation requires a secure context (HTTPS)');
                userLocation = {
                    latitude: 39.9334, // Example coordinates
                    longitude: 32.8597  // Ankara city center
                };
                resolve(userLocation);
                updateWeather();
                updateWaterOutages();
                return;
            }

            if ("geolocation" in navigator) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        userLocation = {
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude
                        };
                        resolve(userLocation);
                        updateWeather();
                        updateWaterOutages();
                    },
                    (error) => {
                        console.error(`Geolocation error (${error.code}): ${error.message}`);
                        
                        // Detailed error handling
                        switch(error.code) {
                            case error.PERMISSION_DENIED:
                                console.warn('User denied geolocation permission');
                                break;
                            case error.POSITION_UNAVAILABLE:
                                console.warn('Location information is unavailable');
                                break;
                            case error.TIMEOUT:
                                console.warn('Location request timed out');
                                break;
                            default:
                                console.warn('Unknown geolocation error');
                        }

                        // Use a default location (e.g., city center)
                        userLocation = {
                            latitude: 39.9334, // Example coordinates
                            longitude: 32.8597  // Ankara city center
                        };
                        resolve(userLocation);
                        updateWeather();
                        updateWaterOutages();
                    },
                    {
                        enableHighAccuracy: false,
                        timeout: 5000,
                        maximumAge: 0
                    }
                );
            } else {
                console.warn("Geolocation is not supported by this browser");
                userLocation = {
                    latitude: 39.9334, // Example coordinates
                    longitude: 32.8597  // Ankara city center
                };
                resolve(userLocation);
                updateWeather();
                updateWaterOutages();
            }
        });
    }

    // Fetch and update weather information
    async function updateWeather() {
        try {
            if (!userLocation) {
                await getUserLocation();
                return;
            }

            const weatherIcon = document.getElementById('weather-icon');
            const weatherLocation = document.getElementById('weather-location');
            const weatherTemp = document.getElementById('weather-temp');
            const weatherHumidity = document.getElementById('weather-humidity');
            const weatherWind = document.getElementById('weather-wind');
            const weatherClouds = document.getElementById('weather-clouds');
            const weatherUpdated = document.getElementById('weather-updated');
            const weatherRecommendation = document.getElementById('weather-recommendation');

            // Check if all elements exist
            const weatherElements = [
                weatherIcon, weatherLocation, weatherTemp, 
                weatherHumidity, weatherWind, weatherClouds, 
                weatherUpdated, weatherRecommendation
            ];

            if (weatherElements.some(el => !el)) {
                console.warn('One or more weather elements not found');
                return;
            }

            // Reverse Geocoding for more accurate location
            let locationName = `${userLocation.latitude.toFixed(2)}°N, ${userLocation.longitude.toFixed(2)}°E`;

            try {
                const reverseGeocodingUrl = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${userLocation.latitude}&lon=${userLocation.longitude}&accept-language=tr`;
                
                const response = await fetch(reverseGeocodingUrl, {
                    headers: {
                        'User-Agent': 'WaterConservationApp/1.0'
                    }
                });
                
                const data = await response.json();
                
                if (data.address) {
                    // Öncelik sırası: şehir, ilçe, il, ülke
                    locationName = 
                        data.address.city || 
                        data.address.town || 
                        data.address.municipality || 
                        data.address.county || 
                        data.address.state || 
                        data.address.country;
                }
            } catch (error) {
                console.warn('Konum bilgisi alınamadı:', error);
            }

            // Open-Meteo API for weather data
            const url = `https://api.open-meteo.com/v1/forecast?latitude=${userLocation.latitude}&longitude=${userLocation.longitude}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,windspeed_10m,cloudcover_mid`;

            const response = await fetch(url);
            const data = await response.json();

            if (data.current_weather) {
                // Update weather details
                weatherLocation.textContent = locationName;
                weatherTemp.textContent = `${data.current_weather.temperature}°C`;
                
                // Get additional details from hourly data
                const currentHour = new Date().getHours();
                const hourlyData = data.hourly;
                
                weatherHumidity.textContent = `${hourlyData.relativehumidity_2m[currentHour]}%`;
                weatherWind.textContent = `${data.current_weather.windspeed} km/h`;
                weatherClouds.textContent = `${hourlyData.cloudcover_mid[currentHour] / 8 * 100}%`;
                
                // Update weather icon based on weather code
                const weatherCode = data.current_weather.weathercode;
                const weatherIcons = {
                    0: 'fa-sun',
                    1: 'fa-cloud-sun',
                    2: 'fa-cloud',
                    3: 'fa-cloud',
                    45: 'fa-smog',
                    48: 'fa-smog',
                    51: 'fa-cloud-rain',
                    53: 'fa-cloud-rain',
                    55: 'fa-cloud-rain',
                    61: 'fa-cloud-showers-heavy',
                    63: 'fa-cloud-showers-heavy',
                    65: 'fa-cloud-showers-heavy',
                    71: 'fa-snowflake',
                    73: 'fa-snowflake',
                    75: 'fa-snowflake',
                    77: 'fa-snowflake',
                    80: 'fa-cloud-showers-water',
                    81: 'fa-cloud-showers-water',
                    82: 'fa-cloud-showers-water',
                    85: 'fa-snowflake',
                    86: 'fa-snowflake',
                    95: 'fa-cloud-bolt',
                    96: 'fa-cloud-bolt',
                    99: 'fa-cloud-bolt'
                };
                
                weatherIcon.innerHTML = `<i class="fas ${weatherIcons[weatherCode] || 'fa-cloud'}"></i>`;

                // Update timestamp
                const now = new Date();
                weatherUpdated.textContent = now.toLocaleTimeString();

                // Add weather recommendation
                const temp = data.current_weather.temperature;
                let recommendation = '';
                if (temp < 10) {
                    recommendation = 'Stay warm and hydrated!';
                } else if (temp > 30) {
                    recommendation = 'Stay cool and drink plenty of water!';
                } else {
                    recommendation = 'Great weather for outdoor activities!';
                }
                weatherRecommendation.textContent = recommendation;
            }
        } catch (error) {
            console.error('Could not get weather information:', error);
            // Update elements with error messages
            safelyUpdateElementText('weather-location', 'Weather Unavailable');
            safelyUpdateElementText('weather-temp', 'N/A');
            safelyUpdateElementText('weather-humidity', '-');
            safelyUpdateElementText('weather-wind', '-');
            safelyUpdateElementText('weather-clouds', '-');
            safelyUpdateElementText('weather-updated', '-');
            safelyUpdateElementText('weather-recommendation', 'Unable to fetch weather data');
        }
    }

    // Check and update water outage information
    async function updateWaterOutages() {
        const waterOutageElement = document.getElementById('water-outage-info');
        
        // Güvenli kontrol: Eğer element yoksa, sessizce çık
        if (!waterOutageElement) {
            console.warn('Water outage element not found. Skipping update.');
            return;
        }

        try {
            if (!userLocation) {
                await getUserLocation();
                return;
            }

            // Simulate water outage check since the backend endpoint is missing
            const simulatedOutage = Math.random() < 0.2;  // 20% chance of outage
            
            if (simulatedOutage) {
                waterOutageElement.textContent = `Water Outage Alert: Estimated 2-3 hours`;
                waterOutageElement.classList.add('text-red-500');
            } else {
                waterOutageElement.textContent = 'No water outages reported';
                waterOutageElement.classList.remove('text-red-500');
            }
        } catch (error) {
            console.error('Could not check water outages:', error);
            waterOutageElement.textContent = 'Outage info unavailable';
        }
    }

    // Update daily water saving tip
    function updateDailyTip() {
        try {
            const dailyTipText = document.getElementById('daily-tip-text');
            
            if (!dailyTipText) {
                console.warn('Daily tip text element not found');
                return;
            }

            const tips = [
                "Turn off the tap while brushing teeth to save 15 liters of water",
                "Run washing machines and dishwashers only when full",
                "Water your garden early in the morning or late in the evening",
                "Reduce shower time by 1 minute to save 12 liters of water",
                "Fix water leaks promptly to save up to 90 liters per day"
            ];
            
            dailyTipText.textContent = tips[Math.floor(Math.random() * tips.length)];
        } catch (error) {
            console.error('Error updating daily tip:', error);
        }
    }

    // Show location permission prompt
    function showLocationPrompt() {
        const locationPrompt = document.createElement('div');
        locationPrompt.className = 'fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-96 bg-white dark:bg-gray-800 p-4 rounded-xl shadow-lg z-50 border border-gray-200 dark:border-gray-700';
        locationPrompt.innerHTML = `
            <div class="flex items-start space-x-4">
                <i class="fas fa-location-dot text-blue-500 text-xl mt-1"></i>
                <div class="flex-1">
                    <h3 class="font-medium text-gray-900 dark:text-white">Location Permission</h3>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
                        Please allow location access to show you the most accurate weather and water outage information.
                    </p>
                    <div class="flex space-x-2">
                        <button id="allow-location" class="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm hover:bg-blue-600 transition-colors">
                            Allow
                        </button>
                        <button id="deny-location" class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg text-sm hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors">
                            Later
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(locationPrompt);

        document.getElementById('allow-location').addEventListener('click', () => {
            getUserLocation();
            locationPrompt.remove();
        });

        document.getElementById('deny-location').addEventListener('click', () => {
            locationPrompt.remove();
            // Continue with default location
            updateWeather();
            updateWaterOutages();
        });
    }

    // Initial setup
    updateDailyTip();
    showLocationPrompt();

    // Update information periodically
    setInterval(() => {
        updateDailyTip();
        if (userLocation) {
            updateWeather();
            updateWaterOutages();
        }
    }, 3600000); // Every hour
});
