import logging
import os

import requests

logger = logging.getLogger(__name__)

def get_weather(city="Bengaluru"):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        logger.error("OPENWEATHER_API_KEY environment variable is not set.")
        return {"error": "OpenWeather API key not configured"}

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        res = response.json()
    except requests.RequestException:
        logger.exception("Weather API request failed for city=%s", city)
        return {"error": "Unable to fetch weather data at the moment"}
    except ValueError:
        logger.exception("Weather API returned non-JSON response for city=%s", city)
        return {"error": "Received unexpected data from weather service"}

    logger.debug("Weather data retrieved for %s: %s", city, res)
    return {
        "city": city,
        "temp": res["main"]["temp"],
        "description": res["weather"][0]["description"]
    }
