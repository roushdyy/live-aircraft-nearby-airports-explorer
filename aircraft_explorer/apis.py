import requests
import csv
import os
from math import radians, sin, cos, sqrt, atan2

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"

def geocode(city_name: str):
    """
    Convert a city name to its latitude and longitude.
    Returns: (latitude, longitude, full_city_name) or (None, None, None)
    """
    params = {
        "name": city_name,
        "count": 1,
        "language": "en",
        "format": "json"
    }
    try:
        response = requests.get(GEOCODE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("results"):
            result = data["results"][0]
            return result["latitude"], result["longitude"], result["name"]
    except Exception as e:
        print(f"[Geocoding Error] {e}")
    return None, None, None
