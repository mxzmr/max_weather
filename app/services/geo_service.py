import requests
import json
from ..errors import WeatherError, WeatherErrorType


class GeoModel:
    name: str = ""
    country: str = ""
    latitude: float = 0
    longitude: float = 0

    def __str__(self):
        return f"name: {self.name}, country: {self.country}"

    @staticmethod
    def get_url(name):
        formatted = name.strip()
        formatted = formatted.replace(" ", "+")
        return f"https://geocoding-api.open-meteo.com/v1/search?name={formatted}&count=1&language=en&format=json"

    def save_country_geo(self, data):
        self.name = data["name"]
        self.country = data["country"]
        self.latitude = data["latitude"]
        self.longitude = data["longitude"]

    geo_moc = {
      "id": 2950159,
      "name": "Berlin",
      "latitude": 52.52437,
      "longitude": 13.41053,
      "elevation": 74.0,
      "feature_code": "PPLC",
      "country_code": "DE"
    }


def fetch(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise WeatherError(WeatherErrorType.CITY_NOT_FOUND, "City not found in geocoding service")
        else:
            raise WeatherError(WeatherErrorType.API_ERROR, 
                             f"Geocoding API error: {response.status_code}")
    except requests.exceptions.ConnectionError:
        raise WeatherError(WeatherErrorType.NETWORK_ERROR, "Could not connect to geocoding service")
    except json.JSONDecodeError:
        raise WeatherError(WeatherErrorType.INVALID_DATA, "Invalid response from geocoding service")

def get_geo(name):
    if not name or not name.strip():
        raise WeatherError(WeatherErrorType.CITY_NOT_FOUND, "Empty city name provided")
    
    geo = GeoModel()
    try:
        json_data = fetch(geo.get_url(name))
        if not json_data.get("results"):
            raise WeatherError(WeatherErrorType.CITY_NOT_FOUND, f"No results found for {name}")
        geo.save_country_geo(json_data["results"][0])
        return geo
    except WeatherError:
        raise
    except Exception as e:
        raise WeatherError(WeatherErrorType.SERVER_ERROR, str(e))

if __name__ == "__main__":
    print(get_geo("haifa"))
