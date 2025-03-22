import requests
import json
from datetime import datetime
from enum import Enum
from app.errors import WeatherError, WeatherErrorType
from app.services.geo_service import get_geo

class WeatherColumn(Enum):
    TEMP_MAX = "temperature_2m_max"
    TEMP_MIN = "temperature_2m_min"
    SUNRISE = "sunrise"
    SUNSET = "sunset"
    SHOWERS = "showers_sum"
    SNOWFALL = "snowfall_sum"
    PRECIP_PROB = "precipitation_probability_max"

class WeatherModel:
    def __init__(self):
        self.daily_data = {}
        
    def parse_response(self, data):
        try:
            daily = data.get('daily', {})
            if not isinstance(daily, dict):
                raise WeatherError(WeatherErrorType.INVALID_DATA, "Invalid daily data format")
                
            time = daily.get('time', [])
            
            # Validate that all required fields exist
            for col in WeatherColumn:
                if col.value not in daily:
                    raise WeatherError(WeatherErrorType.INVALID_DATA, f"Missing {col.value} in response")
            
            formatted_data = []
            for i in range(len(time)):
                day_data = {
                    'date': datetime.strptime(time[i], '%Y-%m-%d').strftime('%B %d'),
                    'temp_max': round(daily[WeatherColumn.TEMP_MAX.value][i]),
                    'temp_min': round(daily[WeatherColumn.TEMP_MIN.value][i]),
                    'sunrise': daily[WeatherColumn.SUNRISE.value][i],
                    'sunset': daily[WeatherColumn.SUNSET.value][i],
                    'showers': daily[WeatherColumn.SHOWERS.value][i],
                    'snowfall': daily[WeatherColumn.SNOWFALL.value][i],
                    'precipitation_prob': daily[WeatherColumn.PRECIP_PROB.value][i]
                }
                formatted_data.append(day_data)
                
            return formatted_data
            
        except (TypeError, ValueError) as e:
            raise WeatherError(WeatherErrorType.INVALID_DATA, str(e))

class WeatherService:
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
    
    def _build_params(self, lat, lon):
        daily_params = ",".join([col.value for col in WeatherColumn])
        return {
            "latitude": lat,
            "longitude": lon,
            "daily": daily_params,
            "timezone": "auto"
        }
    
    def fetch_weather(self, city):
        coordinates = get_geo(city)
        params = self._build_params(coordinates.latitude, coordinates.longitude)
        
        try:
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if not isinstance(data, dict):
                        raise WeatherError(WeatherErrorType.INVALID_DATA, "Invalid JSON response format")
                    return data
                except json.JSONDecodeError:
                    raise WeatherError(WeatherErrorType.INVALID_DATA, "Invalid JSON response")
            elif response.status_code == 404:
                raise WeatherError(WeatherErrorType.CITY_NOT_FOUND)
            else:
                raise WeatherError(
                    WeatherErrorType.API_ERROR,
                    f"Weather API error: {response.status_code}"
                )
        except requests.exceptions.ConnectionError:
            raise WeatherError(WeatherErrorType.NETWORK_ERROR)

def get_weather(city):
    if not city or len(city.strip()) == 0:
        raise WeatherError(WeatherErrorType.CITY_NOT_FOUND)
    
    try:
        weather_service = WeatherService()
        weather_model = WeatherModel()
        
        # Get location data
        geo_data = get_geo(city).__dict__
        
        # Fetch and process weather data
        weather_response = weather_service.fetch_weather(city)
        try:
            geo_data["weather"] = weather_model.parse_response(weather_response)
        except WeatherError:
            raise
        except Exception as e:
            raise WeatherError(WeatherErrorType.INVALID_DATA, str(e))
        return geo_data
        
    except WeatherError:
        raise
    except Exception as e:
        raise WeatherError(WeatherErrorType.SERVER_ERROR, str(e))

if __name__ == "__main__":
    print("today", get_weather("haifa")["name"])
