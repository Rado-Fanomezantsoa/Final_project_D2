import os
from dotenv import load_dotenv

def api_base(latitude, longitude):
    load_dotenv()
    API_KEY = os.getenv("open_weather_api_key")
    return f"http://api.openweathermap.org/data/2.5/air_pollution?lat={latitude}&lon={longitude}&appid={API_KEY}"