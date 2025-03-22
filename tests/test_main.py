import pytest
from unittest.mock import Mock, patch
from app.services.weather_service import get_weather
from app.errors import WeatherError, WeatherErrorType
from app.services.geo_service import GeoModel

@pytest.fixture
def mock_geo_data():
    geo = GeoModel()
    geo.save_country_geo({
        "name": "Test City",
        "country": "Test Country",
        "latitude": 32.0,
        "longitude": 34.0
    })
    return geo

@pytest.fixture
def mock_weather_data():
    return {
        'daily': {
            'time': ['2023-12-01'],
            'temperature_2m_max': [25.5],
            'temperature_2m_min': [15.2],
            'sunrise': ['06:00'],
            'sunset': ['18:00'],
            'showers_sum': [0.5],
            'snowfall_sum': [0],
            'precipitation_probability_max': [30]
        }
    }

@pytest.fixture
def create_mock_response():
    return lambda status_code, json_data: Mock(
        status_code=status_code,
        json=lambda: json_data
    )

@patch('app.services.weather_service.WeatherService.fetch_weather')
@patch('app.services.geo_service.fetch')  # Mock the fetch function
def test_get_weather_success(mock_fetch, mock_fetch_weather, mock_weather_data):
    # Setup geo API mock
    mock_fetch.return_value = {
        "results": [{
            "name": "Test City",
            "country": "Test Country",
            "latitude": 32.0,
            "longitude": 34.0
        }]
    }
    mock_fetch_weather.return_value = mock_weather_data

    result = get_weather('Test City')
    assert result['name'] == 'Test City'
    assert 'weather' in result

@patch('app.services.geo_service.fetch')
def test_get_weather_invalid_api_response(mock_fetch):
    mock_fetch.side_effect = RuntimeError('API Error')
    
    with pytest.raises(WeatherError) as exc_info:
        get_weather("Test City")
    assert exc_info.value.error_type == WeatherErrorType.SERVER_ERROR

@patch('app.services.geo_service.get_geo')
def test_get_weather_invalid_data(mock_get_geo):
    mock_get_geo.return_value = None
    
    with pytest.raises(WeatherError) as exc_info:
        get_weather('Invalid City')
    assert exc_info.value.error_type == WeatherErrorType.CITY_NOT_FOUND

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

@patch('app.services.weather_service.WeatherService.fetch_weather')
@patch('app.services.geo_service.fetch')  # Change to mock fetch instead of get_geo
def test_get_weather_invalid_weather_response(mock_fetch, mock_fetch_weather):
    # Setup geo API mock with valid response
    mock_fetch.return_value = {
        "results": [{
            "name": "Test City",
            "country": "Test Country",
            "latitude": 32.0,
            "longitude": 34.0
        }]
    }
    
    # Setup weather service to return invalid data
    mock_fetch_weather.return_value = {"daily": "invalid"}
    
    with pytest.raises(WeatherError) as exc_info:
        get_weather("Test City")
    assert exc_info.value.error_type == WeatherErrorType.INVALID_DATA  # Changed to INVALID_DATA
