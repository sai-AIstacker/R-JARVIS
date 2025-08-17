import requests
import logging
from livekit.agents import function_tool

# --- Manually set your OpenWeather API key here ---
OPENWEATHER_API_KEY = "a32834e6ef4fd2cc90a20a6d8e8c1259"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jarvis_get_whether")

def detect_city_by_ip() -> str:
    try:
        logger.info("IP के ज़रिए शहर detect करने की कोशिश की जा रही है")
        ip_info = requests.get("https://ipapi.co/json/").json()
        city = ip_info.get("city")
        if city:
            logger.info(f"IP से शहर Detect किया गया: {city}")
            return city
        else:
            logger.warning("City detect करने में विफल, default 'Delhi' इस्तेमाल किया जा रहा है।")
            return "Delhi"
    except Exception as e:
        logger.error(f"IP से city detect करने में error आया: {e}")
        return "Delhi"

@function_tool
async def get_weather(city: str = "") -> str:
    api_key = OPENWEATHER_API_KEY  # <-- Manually set key

    if not api_key:
        logger.error("OpenWeather API key missing है।")
        return "OpenWeather API key नहीं मिली।"

    if not city:
        city = detect_city_by_ip()

    logger.info(f"City के लिए weather fetch किया जा रहा है: {city}")
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "hi"
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            logger.error(f"OpenWeather API में error आया: {response.status_code} - {response.text}")
            return f"Error: {city} के लिए weather fetch नहीं कर पाए। कृपया city name चेक करें।"

        data = response.json()
        weather = data["weather"][0]["description"].title()
        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        result = (f"{city} का मौसम:\n"
                  f"- स्थिति: {weather}\n"
                  f"- तापमान: {temperature}°C\n"
                  f"- नमी: {humidity}%\n"
                  f"- हवा की गति: {wind_speed} m/s")

        logger.info(f"Weather result: \n{result}")
        return result

    except Exception as e:
        logger.exception(f"Weather fetch करते समय exception आया: {e}")
        return "Weather fetch करते समय एक error आया"