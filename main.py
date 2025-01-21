from flask import Flask, render_template, request
from dotenv import load_dotenv
import logging
from .app.services.weather_service import get_weather
from .app.errors import WeatherError, WeatherErrorType, get_user_message
from .app.config import setup_logging

app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static"
    )
load_dotenv()

# Configure logging
logger = setup_logging()

@app.route("/", methods=["GET", "POST"])
def home():
    data = None
    error = None
    if request.method == "POST":
        city = request.form.get("country")
        try:
            data = get_weather(city)
        except WeatherError as e:
            logger.error(f"Weather error: {str(e)} of type {e.error_type}", exc_info=True)
            error = get_user_message(e.error_type)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            error = get_user_message(WeatherErrorType.SERVER_ERROR)
    return render_template("index.html", data=data, error=error)

if __name__ == "__main__":
    app.run(debug=True)
