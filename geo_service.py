import requests
import json


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
    response = requests.get(url)
    if response:
        return response.json()
    else:
        raise Exception(f"Non-success status code: {response.status_code}")

def get_geo(name):
    geo = GeoModel()
    json = fetch(geo.get_url(name))
    
    if json.get("results"):
        geo.save_country_geo(json["results"][0])
        return geo
    return None

if __name__ == "__main__":
    print(get_geo("haifa"))
