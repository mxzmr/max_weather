import pytest
import requests
from unittest.mock import Mock, patch
from datetime import datetime
from app.services.weather_service import WeatherModel, WeatherService, get_weather, WeatherError, WeatherErrorType
from app.services.geo_service import GeoModel

@pytest.fixture
def mock_weather_response():
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
def mock_geo_data():
    data = {
        "name": "Test City",
        "country": "Test Country",
        "latitude": 32.0,
        "longitude": 34.0
    }
    geo_model = GeoModel()
    geo_model.save_country_geo(data)
    return geo_model

class TestWeatherModel:
    def test_parse_response(self, mock_weather_response):
        model = WeatherModel()
        result = model.parse_response(mock_weather_response)
        
        assert len(result) == 1
        assert result[0]['date'] == 'December 01'
        assert result[0]['temp_max'] == 26
        assert result[0]['temp_min'] == 15
        assert result[0]['sunrise'] == '06:00'
        assert result[0]['sunset'] == '18:00'
        assert result[0]['showers'] == 0.5
        assert result[0]['snowfall'] == 0
        assert result[0]['precipitation_prob'] == 30

class TestWeatherService:
    @patch('app.services.geo_service.fetch')  # Mock the fetch function instead
    def test_fetch_weather_success(self, mock_fetch):
        # Setup geo API mock
        mock_fetch.return_value = {
            "results": [{
                "name": "Test City",
                "country": "Test Country",
                "latitude": 32.0,
                "longitude": 34.0
            }]
        }

        service = WeatherService()
        result = service.fetch_weather('test')
        
        assert 'daily' in result
        assert mock_fetch.called

    @patch('requests.get')
    def test_fetch_weather_city_not_found(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        service = WeatherService()
        with pytest.raises(WeatherError) as exc_info:
            service.fetch_weather('NonexistentCity')
        assert exc_info.value.error_type == WeatherErrorType.CITY_NOT_FOUND

    @patch('requests.get')
    def test_fetch_weather_network_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError()

        service = WeatherService()
        with pytest.raises(WeatherError) as exc_info:
            service.fetch_weather('Test City')
        assert exc_info.value.error_type == WeatherErrorType.NETWORK_ERROR

    def test_build_params(self):
        service = WeatherService()
        params = service._build_params(32.0, 34.0)
        
        assert params['latitude'] == 32.0
        assert params['longitude'] == 34.0
        assert 'temperature_2m_max' in params['daily']
        assert 'timezone' in params

class TestGetWeather:
    @patch('app.services.weather_service.WeatherService.fetch_weather')
    @patch('app.services.geo_service.fetch')  # Mock the fetch function
    def test_get_weather_success(self, mock_fetch, mock_fetch_weather, mock_weather_response):
        # Setup geo API mock
        mock_fetch.return_value = {
            "results": [{
                "name": "Test City",
                "country": "Test Country",
                "latitude": 32.0,
                "longitude": 34.0
            }]
        }
        mock_fetch_weather.return_value = mock_weather_response

        result = get_weather('Test City')
        
        assert result['name'] == 'Test City'
        assert 'weather' in result
        assert len(result['weather']) == 1

    def test_get_weather_empty_city(self):
        with pytest.raises(WeatherError) as exc_info:
            get_weather('')
        assert exc_info.value.error_type == WeatherErrorType.CITY_NOT_FOUND

    @patch('app.services.geo_service.get_geo')
    def test_get_weather_geo_error(self, mock_get_geo):
        mock_get_geo.side_effect = WeatherError(WeatherErrorType.CITY_NOT_FOUND)
        
        with pytest.raises(WeatherError) as exc_info:
            get_weather('NonexistentCity')
        assert exc_info.value.error_type == WeatherErrorType.CITY_NOT_FOUND

    @patch('app.services.geo_service.fetch')
    def test_get_weather_unexpected_error(self, mock_fetch):
        mock_fetch.side_effect = RuntimeError('Unexpected error')
        
        with pytest.raises(WeatherError) as exc_info:
            get_weather('Test City')
        assert exc_info.value.error_type == WeatherErrorType.SERVER_ERROR
