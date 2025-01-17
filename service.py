import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import geo_service as geo
from enum import Enum


# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

weather_moc = {
        "latitude": 52.52,
        "longitude": 13.419,
        "elevation": 44.812,
        "generationtime_ms": 2.2119,
        "timezone": "Europe/Berlin",
        "timezone_abbreviation": "CEST",
        "hourly": {
            "time": ["2022-07-01T00:00",
                     "2022-07-01T01:00",
                     "2022-07-01T02:00"],
            "temperature_2m":
            [13, 12.7, 12.7, 12.5, 12.5, 12.8, 13, 12.9, 13.3],
        },
        "hourly_units": {
            "temperature_2m": "°C"
        }
    }


class WeatherColumn(Enum):
    """
    Holds hourly parameters values for columns
    its used when formating the data form the api
    it should contain all the columns needed for formating
    """
    TEMP = "temperature_2m"
    HUMID = "relative_humidity_2m"

def fetch_weather(city):
    coordinates = geo.get_geo(city)
    print((coordinates.__dict__))
    # Define API URL and parameters
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coordinates.latitude,
        "longitude": coordinates.longitude,
        "hourly": f"{WeatherColumn.TEMP.value},{WeatherColumn.HUMID.value}",
    }

    # Fetch weather data
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    return response

def format_weather(response):
    # Extract hourly data
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_humidity_2m = hourly.Variables(1).ValuesAsNumpy()

    # Create a DataFrame with hourly data
    hourly_data = {
        "time": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ),
        WeatherColumn.TEMP.value: hourly_temperature_2m,
        WeatherColumn.HUMID.value: hourly_humidity_2m,
    }
    hourly_dataframe = pd.DataFrame(data=hourly_data)

    # Aggregate hourly data into daily summaries
    daily_dataframe = hourly_dataframe.resample("D", on="time").agg({
        WeatherColumn.TEMP.value: ["max", "min", "mean"],
        WeatherColumn.HUMID.value: ["mean"],
    })
    daily_dataframe.columns = ["_".join(col) for col in daily_dataframe.columns]  # Flatten MultiIndex columns
    daily_dataframe.reset_index(inplace=True)  # Changed from False to True
    
    # Add formatted date
    daily_dataframe['date'] = daily_dataframe['time'].dt.strftime('%B %d')
    
    daily_dataframe = daily_dataframe.map(lambda x: int(x) if isinstance(x, (int, float)) else x)
    daily_data_json = daily_dataframe.to_dict(orient="records")
    return daily_data_json 


def get_weather(city):
    weather_data = fetch_weather(city)
    print("weather", type(format_weather(weather_data)))
    geo_data = geo.get_geo(city).__dict__
    geo_data["weather"] = format_weather(weather_data) 
    print("geo", type(geo_data))
    return geo_data 
if __name__ == "__main__":
    print("today", get_weather("haifa")["name"])
