import pytest
import requests
from unittest.mock import Mock, patch
from app.services.geo_service import GeoModel, fetch, get_geo
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
def geo_model():
    return GeoModel()

class TestGeoModel:
    def test_init(self, geo_model):
        assert geo_model.name is None
        assert geo_model.country is None
        assert geo_model.latitude is None
        assert geo_model.longitude is None

    def test_str(self, geo_model):
        geo_model.name = "Test City"
        geo_model.country = "Test Country"
        assert str(geo_model) == "name: Test City, country: Test Country"

    def test_get_url(self):
        url = GeoModel.get_url("New York")
        assert "name=New+York" in url
        assert "count=1" in url
        
        # Test URL with spaces
        url = GeoModel.get_url("San Francisco")
        assert "name=San+Francisco" in url

    def test_save_country_geo(self, geo_model):
        data = {
            "name": "Test City",
            "country": "Test Country",
            "latitude": 32.0,
            "longitude": 34.0
        }
        geo_model.save_country_geo(data)
        
        assert geo_model.name == "Test City"
        assert geo_model.country == "Test Country"
        assert geo_model.latitude == 32.0
        assert geo_model.longitude == 34.0

class TestFetch:
    @patch('requests.get')
    def test_fetch_success(self, mock_get, mock_geo_response):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_geo_response
        mock_get.return_value = mock_response

        result = fetch("test_url")
        assert result == mock_geo_response

    @patch('requests.get')
    def test_fetch_city_not_found(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with pytest.raises(WeatherError) as exc_info:
            fetch("test_url")
        assert exc_info.value.error_type == WeatherErrorType.CITY_NOT_FOUND

    @patch('requests.get')
    def test_fetch_network_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError()

        with pytest.raises(WeatherError) as exc_info:
            fetch("test_url")
        assert exc_info.value.error_type == WeatherErrorType.NETWORK_ERROR

    @patch('requests.get')
    def test_fetch_invalid_json(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        with pytest.raises(WeatherError) as exc_info:
            result = fetch("test_url")
        assert exc_info.value.error_type == WeatherErrorType.INVALID_DATA
        assert "Invalid JSON" in str(exc_info.value)  # Changed from exc_info.value.message to str(exc_info.value)

class TestGetGeo:
    @patch('app.services.geo_service.fetch')
    def test_get_geo_success(self, mock_fetch, mock_geo_response):
        mock_fetch.return_value = mock_geo_response

        result = get_geo("Test City")
        
        assert result.name == "Test City"
        assert result.country == "Test Country"
        assert result.latitude == 32.0
        assert result.longitude == 34.0

    def test_get_geo_empty_name(self):
        with pytest.raises(WeatherError) as exc_info:
            get_geo("")
        assert exc_info.value.error_type == WeatherErrorType.CITY_NOT_FOUND

    @patch('app.services.geo_service.fetch')
    def test_get_geo_no_results(self, mock_fetch):
        mock_fetch.return_value = {"results": []}

        with pytest.raises(WeatherError) as exc_info:
            get_geo("NonexistentCity")
        assert exc_info.value.error_type == WeatherErrorType.CITY_NOT_FOUND

    @patch('app.services.geo_service.fetch')
    def test_get_geo_unexpected_error(self, mock_fetch):
        mock_fetch.side_effect = Exception("Unexpected error")

        with pytest.raises(WeatherError) as exc_info:
            get_geo("Test City")
        assert exc_info.value.error_type == WeatherErrorType.SERVER_ERROR
