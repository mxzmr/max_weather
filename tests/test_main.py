import pytest
from unittest.mock import patch, Mock
from app.services.service import get_weather
from app.services.geo_service import GeoModel
from app.errors import WeatherError, WeatherErrorType

@pytest.fixture
def mock_geo_response():
    return {
        "results": [{
            "name": "Test City",
            "country": "Test Country",
            "latitude": 32.0,
            "longitude": 34.0
        }]
    }

@pytest.fixture
def mock_weather_response():
    return {
        "daily": {
            "time": ["2024-01-01"],
            "temperature_2m_max": [25.0],
            "temperature_2m_min": [15.0],
            "sunrise": ["2024-01-01T06:00"],
            "sunset": ["2024-01-01T18:00"],
            "showers_sum": [0.0],
            "snowfall_sum": [0.0],
            "precipitation_probability_max": [20]
        }
    }

@pytest.fixture
def create_mock_response():
    return lambda status_code, json_data: Mock(
        status_code=status_code,
        json=lambda: json_data
    )

@patch('requests.get')
@patch('app.services.geo_service.get_geo')
def test_get_weather_success(mock_geo, mock_get, create_mock_response, mock_weather_response):
    # Setup geo mock
    geo_model = GeoModel()
    geo_model.name = "Test City"
    geo_model.country = "Test Country"
    geo_model.latitude = 32.0
    geo_model.longitude = 34.0
    mock_geo.return_value = geo_model
    
    # Simpler mock setup
    mock_get.return_value = create_mock_response(200, mock_weather_response)
    
    result = get_weather("Test City")
    
    assert result["name"] == "Test City"
    assert result["country"] == "Test Country"
    assert len(result["weather"]) == 1
    assert result["weather"][0]["temp_max"] == 25
    assert result["weather"][0]["temp_min"] == 15

def test_get_weather_empty_city():
    # No mocks needed for this test
    with pytest.raises(WeatherError) as exc_info:
        get_weather("")
    assert exc_info.value.error_type == WeatherErrorType.CITY_NOT_FOUND

@patch('requests.get')
def test_get_weather_city_not_found(mock_get, create_mock_response):
    mock_get.return_value = create_mock_response(200, {"results": []})
    
    with pytest.raises(WeatherError) as exc_info:
        get_weather("NonexistentCity")
    assert exc_info.value.error_type == WeatherErrorType.CITY_NOT_FOUND

@patch('requests.get')
def test_get_weather_network_error(mock_get):
    mock_get.side_effect = Exception("Network error")
    
    with pytest.raises(WeatherError) as exc_info:
        get_weather("Test City")
    assert exc_info.value.error_type == WeatherErrorType.SERVER_ERROR

@patch('requests.get')
@patch('app.services.geo_service.get_geo')
def test_get_weather_invalid_data(mock_geo, mock_get, create_mock_response):
    # Setup geo mock
    geo_model = GeoModel()
    geo_model.name = "Test City"
    geo_model.country = "Test Country"
    geo_model.latitude = 32.0
    geo_model.longitude = 34.0
    mock_geo.return_value = geo_model
    
    mock_get.return_value = create_mock_response(200, {"daily": "invalid"})
    
    with pytest.raises(WeatherError) as exc_info:
        get_weather("Test City")
    assert exc_info.value.error_type == WeatherErrorType.SERVER_ERROR
