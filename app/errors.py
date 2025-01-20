from enum import Enum

class WeatherErrorType(Enum):
    CITY_NOT_FOUND = "CITY_NOT_FOUND"
    SERVER_ERROR = "SERVER_ERROR"
    INVALID_DATA = "INVALID_DATA"
    NETWORK_ERROR = "NETWORK_ERROR"
    API_ERROR = "API_ERROR"
    FETCH_ERROR = "FETCH_ERROR"  # Add this line

class WeatherError(Exception):
    def __init__(self, error_type, message=None):
        self.error_type = error_type
        super().__init__(message if message else str(error_type))

def get_user_message(error_type: WeatherErrorType) -> dict:
    messages = {
        WeatherErrorType.CITY_NOT_FOUND: {
            "heading": "City Not Found",
            "message": "We couldn't find the city you entered. Please check your spelling and try again."
        },
        WeatherErrorType.SERVER_ERROR: {
            "heading": "Server Error",
            "message": "We're experiencing technical difficulties. Please try again later."
        },
        WeatherErrorType.INVALID_DATA: {
            "heading": "Invalid Data Received",
            "message": "We received invalid data from the weather service. Please try again later."
        },
        WeatherErrorType.NETWORK_ERROR: {
            "heading": "Connection Error",
            "message": "We couldn't connect to the weather service. Please check your internet connection and try again."
        },
        WeatherErrorType.API_ERROR: {
            "heading": "Service Unavailable",
            "message": "The weather service is currently unavailable. Please try again later."
        }
    }
    return messages.get(error_type, {
        "heading": "Unexpected Error",
        "message": "An unexpected error occurred. Please try again later."
    })
