import requests
import os

API_KEY = os.getenv("OPENWEATHER_API_KEY")

def run(user_input=None, **kwargs):
    if user_input and "weather" in user_input.lower():
        parts = user_input.lower().split()
        city = parts[-1]
        try:
            resp = requests.get(
                f"http://api.openweathermap.org/data/2.5/weather",
                params={"q": city, "appid": API_KEY, "units": "metric"}
            ).json()
            desc = resp["weather"][0]["description"]
            temp = resp["main"]["temp"]
            return f"Weather in {city}: {desc}, {temp}°C"
        except Exception as e:
            return f"Cannot fetch weather: {e}"
    return None
